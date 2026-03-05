# OMEGA v61 Google Cloud 迁移与重构规划

> [!NOTE]
> 核心思路：**存储与计算分离（Decoupled Storage and Compute）** 与 **按需弹性（Elastic On-Demand）**。摒弃“买一台固定大机器一直开着”的思维，转而在需要海量算力时瞬间召唤云端集群，任务结束立即释放。保留 Mac Studio 作为总控台（Control Plane）。

## 1. 数据存储方案：云端数据湖 (Data Lake)

**不要将 2.6TB 的 Level-2 数据存放在虚拟机的挂载云硬盘（Persistent Disk）上。**
直接将 `data/level2` 的所有 `.7z` 压缩包和生成的 `.parquet` 文件存放在 **Google Cloud Storage (GCS)** 的 Standard bucket 中。

- **成本优势**：2.6TB 数据在 GCS Standard 存储每月仅需约 \$50-\$60。如果放在大容量 SSD 云硬盘上，每月需额外支付大笔费用。
- **性能优势**：GCS 可以支持成百上千个计算节点同时满载并发读取，带宽极高。
- **操作方式**：通过 `gcsfuse` 将 GCS Bucket 挂载为本地目录，或者直接在 Polars 中使用 `pl.scan_parquet("gs://omega_pool/...")`。

## 2. 计算层重构：V61 架构适配

当前 v61 架构分为三大步：**Framing（提取特征）** -> **Base Matrix 集成** -> **ML Training（模型训练）**。
以下是针对每一步的 GCP 云原生改造建议：

### 阶段一：Framing 海量并发提取 (The Heavy I/O Task)

目前你把 751 个文件通过 MD5 哈希强制分片给了 Linux (Ryzen) 和 Windows 两个节点，还遇到了 ZFS 内存泄漏死锁问题。
在 GCP 上，我们使用 **Google Cloud Batch** (或动态分配的一组 **Spot VMs**)。

- **方案**：不需要预先配置异构节点。写一个脚本模板 `v61_gcp_framing.py`。
- **执行**：向 GCP 发送一个 Batch Job 指令：“给我启动 20 台 `n2-standard-16` (Spot 抢占式实例，比常规价格便宜 60-90%)，将总文件划分为 20 个 Shard。每台机器领走自己的 Shard 索引，从 GCS 下载相关的 7z 文件，解压，用 Polars 算完特征，把生成的 `.parquet` 存回 GCS，然后**自动销毁结账**。”
- **改造点**：修改现有的 `--shard` 参数逻辑，直接读取 Cloud Batch 传入的环境变量 `BATCH_TASK_INDEX`，并用 `gcsfs` 读写网络存储。再也不用担心 126G 内存爆掉导致系统离线。

### 阶段二：Forge Base Matrix 集成

- **方案**：使用一台临时的高内存实例（例如 `m3-ultramem-32` 拥有近 1TB 内存，或者 `n2-highmem-64`，视合并后的数据集大小而定）。
- **执行**：这台机器开机只活 30 分钟。运行 `v60_forge_base_matrix.py`，将 GCS 里的几百个 parquet 文件合并、清洗、Join 宏观数据后，写出最终的 `base_matrix.parquet` 回到 GCS。然后立刻关机。

### 阶段三：XGBoost 模型训练 (Training)

- **现状**：我看到你的代码库里已经有了 `tools/run_vertex_xgb_train.py` 和 `tools/submit_vertex_sweep.py`。这说明你已经涉足了 Vertex AI。
- **加强**：继续坚持使用 **GCP Vertex AI Custom Training**。这是最完美的 Serverless 训练方案。你只需要从 Mac 主控端发起请求，Vertex 会自动启动自带 GPU（或超大 CPU）的容器，从 GCS 读取 `base_matrix.parquet`，跑完训练，把 `.pkl` 模型写回 GCS。这个环节不需要租任何基础 VM。

## 3. 日常开发与回测环境 (Dev & Backtester Workspace)

既然重负荷任务都被扔给了 Cloud Batch 和 Vertex AI，你还需要在 GCP 租用一台长期的 VM 吗？

**答案：视网络延迟而定。**
由于你是把 OMEGA 当作一个严肃的交易系统在开发：

1. **轻量级云端跳板机 (Jumpbox/Devbox)**：建议租用一台 `e2-standard-4` 或 `n2-standard-8` (16-32GB RAM)，挂一块 100GB 的常用盘。装好 VS Code Server、Tmux。你可以用它来连接 GCP 内网，快速用 Polars 验证少量云端 Parquet 代码，测试回测逻辑。这台机器可以**随用随开**，不工作时关闭以节省费用。
2. **Mac Studio 作为总控台**：你的 M4 Max 本地算力和体验极佳，依然可以作为本地的主 IDE 和 Git Master 节点。所有对 GCP 资源的调度（如发起 Batch Job，提交 Vertex 训练，下载生成的模型），都可以通过 `gcloud` CLI 或 Python API 在 Mac 上一键执行。

## 4. 迁移执行路线图 (Execution Roadmap)

若决定实施，我（AI）将协助你完成以下实质性代码改造：

1. **改造 `v61_framing.py`**：剔除特定于操作系统的本地路径逻辑，引入 `google-cloud-storage` + `fsspec`。使代码能在任意全新的 Ubuntu 云容器内基于 `gs://` 路径无缝跑通。
2. **编写 Dockerfile**：把 OMEGA 的环境（包括 Polars, XGBoost, 7zip）打包成一个标准的 Docker 镜像，推送到 Google Artifact Registry。
3. **编写 Cloud Batch 提交脚本**：在 Mac 端写一个 `submit_framing_job.py`，一键启动成百上千个容器在云端进行 Level-2 提取。
4. **数据极速上云**：协助你利用 `gsutil -m cp` 等多线程工具，最大化利用带宽，把本地的 2.6TB `/omega_pool` 快速迁移至 GCS Bucket。

## 本次审计结论

- **是否需要长期租用昂贵的巨型 VM？** **绝对不需要**。如果一直开着一台 128核/512G 的机器，哪怕不用也会产生巨额账单。
- **最佳范式**：通过 Docker 镜像 + GCS + Cloud Batch + Vertex AI，将 OMEGA V61 真正化身云原生量化计算引擎。所有的开销将严格与其实际运行时间成正比。
