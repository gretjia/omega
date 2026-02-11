
import os

user_input = """
算力芯片,寒武纪,688256,国产AI芯片全栈领军者，自主可控核心标的。
,海光信息,688041,国产x86 CPU+DCU双轮驱动，生态兼容性最强。
,龙芯中科,688047,坚持自主指令集，长期主义者的选择。
,澜起科技,688008,内存接口芯片全球双寡头，受益DDR5/HBM渗透。
,景嘉微,300474,国产图形GPU稀缺标的，信创市场主力。
制造/封测,北方华创,002371,半导体设备全能王，国产替代中流砥柱。
,中微公司,688012,刻蚀设备全球领先，管理层技术背景深厚。
,拓荆科技,688072,薄膜沉积设备龙头，技术壁垒极高。
,长电科技,600584,封测全球第三，掌握先进封装技术。
,通富微电,002156,深度绑定AMD，享受全球AI算力外溢红利。
光通信(CPO),中际旭创,300308,全球光模块龙头，800G/1.6T份额领先。
,新易盛,300502,快速切入海外云巨头，LPO技术先锋。
,天孚通信,300394,光引擎与无源器件隐形冠军，盈利能力极强。
,光库科技,300620,铌酸锂调制器稀缺标的，CPO关键技术储备。
,太辰光,300570,MPO光纤连接器龙头，海外营收占比高。
,华工科技,000988,硅光技术先行者，光模块国产化主力。
算力硬件,沪电股份,002463,AI服务器/交换机PCB龙头，技术积淀深厚。
,胜宏科技,300476,英伟达显卡PCB核心供应商，业绩弹性大。
,深南电路,002916,封装基板国家队，PCB与基板双轮驱动。
,工业富联,601138,全球AI服务器代工霸主，绑定英伟达。
,浪潮信息,000977,国内服务器出货量第一，渠道优势明显。
,中科曙光,603019,芯片+整机+云全栈布局，信创首选。
液冷/能源,英维克,002837,精密温控全链条龙头，液冷技术引领者。
,飞龙股份,002536,电子水泵跨界成功，服务器液冷新势力。
,高澜股份,300499,专注于水冷产品，数据中心液冷先驱。
,国电南瑞,600406,智能电网龙头，虚拟电厂核心技术方。
边缘/终端,瑞芯微,603893,AIoT SoC龙头，边缘算力核心标的。
,晶晨股份,688099,多媒体SoC龙头，拓展汽车与海外市场。
,恒玄科技,688608,智能穿戴音频芯片，端侧AI入口。
,全志科技,300458,智能硬件SoC，AI下沉市场推动者。
,德赛西威,002920,智能驾驶域控龙头，深度绑定英伟达与理想。
,中科创达,300496,智能操作系统专家，连接芯片与应用。
,立讯精密,002475,消费电子精密制造龙头，AI硬件核心代工。
,传音控股,688036,新兴市场手机之王，AI下沉市场推动者。
具身智能,三花智控,002050,特斯拉机器人执行器核心供应商。
,绿的谐波,688017,谐波减速器国产替代龙头。
,鸣志电器,603728,空心杯电机全球领先，灵巧手关键部件。
,北特科技,603009,行星滚柱丝杠工艺领先，产能布局积极。
,双环传动,002472,减速器全谱系龙头，RV减速器强。
AI应用,金山办公,688111,WPS AI落地迅速，订阅制商业模式优质。
,科大讯飞,002230,语音与认知大模型国家队，应用落地广。
,同花顺,300033,金融AI龙头，拥有海量C端用户数据。
,恒生电子,600570,证券IT龙头，B端金融AI底座。
,卫宁健康,300253,医疗信息化+AI，WiNGPT模型垂直深耕。
,宝信软件,600845,钢铁信息化+IDC双龙头，国企改革标杆。
,柏楚电子,688188,激光切割控制系统垄断者，高毛利高成长。
,万兴科技,300624,AIGC创意软件出海龙头，拥抱Sora技术。
,昆仑万维,300418,游戏+平台+大模型全方位布局，弹性大。
,三七互娱,002555,AI赋能游戏研运，降本增效显著。
数据要素,易华录,300212,数据湖基础设施，央企数据收储平台。
,深桑达A,000032,中国电子云运营方，政务数据核心。
,太极股份,002368,政务云与数据服务老牌国家队。
,人民网,603000,数据确权与内容风控的权威平台。
"""

existing_pool = """
# OMEGA TARGET POOL
# Format: [Code] [Name] # [Tag] Reason

# --- Previous Batch ---
300331 # 苏大维格 (待确认)
603986 # 兆易创新 (待确认)
688521 # 芯原股份 (待确认)
301421 # 波长光电
300476 # 胜宏科技 (待确认)
300857 # 协创数据 (待确认)
301396 # 宏景科技 (待确认)
688183 # 生益电子 (待确认)
002008 # 大族激光 (待确认)
300570 # 太辰光 (待确认)
603228 # 景旺电子
688068 # 热景生物
301200 #大族数控
688502 #茂莱光学
301392 # 汇成真空
688141 #杰华特
002655 # 共达电声
603800 #洪田股份
"""

def parse_input(text):
    stocks = []
    current_category = "General"
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line: continue
        
        parts = line.split(',')
        if len(parts) >= 4:
            # Full line: Category, Name, Code, Reason
            category = parts[0].strip()
            name = parts[1].strip()
            code = parts[2].strip()
            reason = parts[3].strip()
            if category: 
                current_category = category
            
            stocks.append({
                "code": code,
                "name": name,
                "category": current_category,
                "reason": reason
            })
            
        elif len(parts) == 4 and parts[0] == "": # Continuation
             pass # Handled above by strict index check?
             # Actually split gives empty string for first part
             
    return stocks

def parse_existing(text):
    stocks = []
    for line in text.split('\n'):
        line = line.strip()
        if not line or line.startswith("#"): continue
        
        # 300331 # 苏大维格 (待确认)
        parts = line.split('#')
        code = parts[0].strip()
        rest = parts[1].strip() if len(parts) > 1 else ""
        
        # Heuristic parse name
        # "苏大维格 (待确认)"
        name = rest.split(' ')[0]
        
        stocks.append({
            "code": code,
            "name": name,
            "category": "Legacy",
            "reason": rest
        })
    return stocks

def main():
    # 1. Parse New Input
    new_stocks = []
    current_category = "General"
    lines = user_input.strip().split('\n')
    
    for line in lines:
        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 3: continue
        
        # Case 1: Category, Name, Code, Reason
        # Case 2: , Name, Code, Reason
        
        if parts[0]:
            current_category = parts[0]
            
        name = parts[1]
        code = parts[2]
        reason = parts[3] if len(parts) > 3 else ""
        
        new_stocks.append({
            "code": code,
            "name": name,
            "category": current_category,
            "reason": reason
        })

    # 2. Parse Existing
    existing_stocks = parse_existing(existing_pool)
    
    # 3. Merge (New overrides Old)
    final_map = {}
    
    # Add new first (priority)
    for s in new_stocks:
        final_map[s['code']] = s
        
    # Add existing if not present
    for s in existing_stocks:
        if s['code'] not in final_map:
            final_map[s['code']] = s
            
            
    # 4. Generate Output
    active_limit = 50
    all_codes = list(final_map.keys())
    
    # Sort key: Put new/categorized ones first? 
    # Or keep original order?
    # Let's keep new input order, then append leftovers
    
    ordered_list = []
    seen = set()
    
    for s in new_stocks:
        if s['code'] not in seen:
            ordered_list.append(s)
            seen.add(s['code'])
            
    for s in existing_stocks:
        if s['code'] not in seen:
            ordered_list.append(s)
            seen.add(s['code'])
            
    print(f"Total Unique Stocks: {len(ordered_list)}")
    
    with open("pool_updated.md", "w") as f:
        f.write("# OMEGA TARGET POOL\n")
        f.write("# Format: [Code] [Name] # [Tag] Reason\n\n")
        
        f.write("# --- ACTIVE COMBAT POOL (Limit 50) ---\n")
        
        count = 0
        for s in ordered_list:
            if count < active_limit:
                line = f"{s['code']} {s['name']} # [{s['category']}] {s['reason']}\n"
                f.write(line)
                count += 1
            else:
                if count == active_limit:
                     f.write("\n# --- WAITLIST (In excess of 50) ---\n")
                line = f"# {s['code']} {s['name']} # [{s['category']}] {s['reason']}\n"
                f.write(line)
                count += 1

if __name__ == "__main__":
    main()
