## 回答：现有 trainer.py 是否有效利用硬件、能否并行
- 现有 [trainer.py](file:///d:/Omega_vNext/trainer.py) 训练链路主要是单进程串行（按文件读取→按窗口提特征→主进程 partial_fit），对你这台 Ryzen + 128GB + NVMe 的利用率偏低（尤其多核与内存）。
- 可以并行，但必须遵守“不改变训练质量/不打乱时序”的约束：
  - 不能并行更新同一个 SGD 模型（会引入竞态与不可控差异）。
  - 只能并行“重计算”（读CSV、生成bars、提特征、算标签），再由主进程按原顺序回放给模型。

## 新约束（你最新要求）
- 不停止当前后台单线程训练（terminal 4 那个进程继续跑）。
- 不修改任何现有文件（根目录与现有模块都不动）。
- 在根目录新建一个独立目录 `./parallel_trainer/`，所有并行训练相关代码只新增在这里。
- 暂不做测试/对照跑（因为单线程训练未完成）。

## 方案：在 ./parallel_trainer 内新增“无损并行”训练器
### 并行原则（质量保证）
- **不变量**：文件顺序、单文件窗口顺序、batch 切分顺序、scaler/model 的 partial_fit 调用顺序保持与当前串行逻辑一致。
- **实现手段**：
  - 使用 `ProcessPoolExecutor.map`（有序返回）并行计算每个文件的 (X,y,w)。
  - 主进程按 map 的输出顺序回放到 `partial_fit`。
  - worker 只做纯函数计算，不接触模型对象。
- **数值可复现控制**：worker 内设置 BLAS/OpenMP 线程=1，避免多线程浮点路径引入差异。

### 目录结构（新增文件）
- `parallel_trainer/README.md`
  - 说明用途、与原 trainer.py 的关系、如何运行、并行参数、注意事项（Windows spawn）。
- `parallel_trainer/parallel_config.py`
  - 并行参数：workers、prefetch_files、worker_threads、是否启用二进制缓存、日志路径等。
- `parallel_trainer/parallel_dataflow.py`
  - worker 端函数：
    - `process_file_to_batches(fp, kernel_cfg, trainer_cfg, src_cfg) -> list[Batch]` 或生成器
    - 严格复用现有逻辑：read_tick_csv → tickdata_to_bars → iter_samples_from_bars → label → pack.values
  - 返回 numpy 数组 (X,y,w)（不返回大量 Python 对象）。
- `parallel_trainer/parallel_trainer.py`
  - `ParallelOmegaTrainer`：复制/镜像现有 OmegaTrainer 的 fit/calibrate 结构，但把“按文件循环”替换为 ordered parallel prefetch。
  - 仍然产出同样的 artifacts 格式（写到 `./artifacts/omega_policy_parallel.pkl` 或可配置名称）。
- `parallel_trainer/run_parallel.py`
  - CLI 入口：加载 [config.py](file:///d:/Omega_vNext/config.py) 的 KernelConfig 与现有 TrainerConfig（或复用 trainer.py 的 example_trainer_config），调用 ParallelOmegaTrainer。

### Calibration 并行化（无损）
- worker 并行计算每个文件的 S/H 序列（按窗口顺序）
- 主进程按文件顺序逐条 `ReservoirSampler.add()`（顺序一致→阈值一致性最好）

### Training 并行化（无损）
- worker 并行生成每文件的 (X,y,w)
- 主进程按顺序将这些数组切成 batch_size 子块并 `_partial_fit`

## 预期加速（不测试前的估计）
- Calibration：4×–12×（常见 6×–10×）
- 总训练：2×–6×（常见 3×–5×）

## 等单线程训练完成后再做的验证（这一步先不执行）
- 串行 vs 并行：校准阈值一致性、训练后 coef_ 差异、总耗时与CPU利用率。

如果你确认这个计划，我会在不触碰现有文件的前提下，只新增 `./parallel_trainer/` 目录及上述文件，并且不启动并行训练、不做测试，直到你明确让它开始跑。