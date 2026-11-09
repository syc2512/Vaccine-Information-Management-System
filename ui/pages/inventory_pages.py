# 疫苗入库相关页面

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

try:
    from config.settings import VACCINE_TYPES, STORAGE_KEYWORDS
except ImportError:
    # 如果导入失败，使用硬编码的默认值
    VACCINE_TYPES = [
        '', '灭活疫苗（死疫苗）', '减毒活疫苗', '类毒素疫苗',
        '亚单位 / 组分疫苗', '重组蛋白疫苗',
        '多糖疫苗与结合疫苗', '病毒载体疫苗',
        '核酸疫苗（DNA/RNA 疫苗）', '病毒样颗粒疫苗 (VLP)', '其他疫苗'
    ]
    STORAGE_KEYWORDS = [
        '避光保存', '不可倒置', '防潮', '防热',
        '防震', '轻拿轻放', '密封保存', '避免阳光直射',
        '不可冷冻', '不可冷藏'
    ]


def render_single_inventory(parent, service):
    # 单个疫苗入库登记

    def show_single_inventory_form():
        # 内部函数
        # 标题
        title = tk.Label(parent, text='单个疫苗入库登记', 
                        font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
        title.pack(pady=20)
        
        # 创建表单框架
        form_frame = tk.Frame(parent, bg='#FFFFFF', padx=40)
        form_frame.pack(pady=10, fill=tk.X)
        
        # 疫苗编号
        tk.Label(form_frame, text='疫苗编号：', font=('SimHei', 12), 
                bg='#FFFFFF').grid(row=0, column=0, sticky=tk.W, pady=5)
        id_var = tk.StringVar()
        id_entry = tk.Entry(form_frame, textvariable=id_var, 
                           font=('SimHei', 12), width=25)
        id_entry.grid(row=0, column=1, pady=5)
        
        # 疫苗名称
        tk.Label(form_frame, text='疫苗名称：', font=('SimHei', 12), 
                bg='#FFFFFF').grid(row=1, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = tk.Entry(form_frame, textvariable=name_var, 
                             font=('SimHei', 12), width=25)
        name_entry.grid(row=1, column=1, pady=5)
        
        # 类别
        tk.Label(form_frame, text='类别：', font=('SimHei', 12), 
                bg='#FFFFFF').grid(row=2, column=0, sticky=tk.W, pady=5)
        
        category_var = tk.StringVar()
        category_menu = tk.OptionMenu(form_frame, category_var, *VACCINE_TYPES)
        category_menu.config(font=('SimHei', 12), width=22, bg='white')
        category_menu.grid(row=2, column=1, pady=5)
        
        # 生产日期
        tk.Label(form_frame, text='生产日期：', font=('SimHei', 12),
                bg='#FFFFFF').grid(row=8, column=0, sticky=tk.W, pady=5)
        prod_date_var = tk.StringVar()
        prod_date_entry = tk.Entry(form_frame, textvariable=prod_date_var,
                                 font=('SimHei', 12), width=25)
        prod_date_entry.insert(0, '2026-01-01')
        prod_date_entry.grid(row=8, column=1, pady=5)
        
        # 有效期
        tk.Label(form_frame, text='有效期至：', font=('SimHei', 12),
                bg='#FFFFFF').grid(row=9, column=0, sticky=tk.W, pady=5)
        expiry_date_var = tk.StringVar()
        expiry_date_entry = tk.Entry(form_frame, textvariable=expiry_date_var,
                                   font=('SimHei', 12), width=25)
        expiry_date_entry.insert(0, '2026-12-31')
        expiry_date_entry.grid(row=9, column=1, pady=5)
        
        # 生产厂家
        tk.Label(form_frame, text='生产厂家：', font=('SimHei', 12),
                bg='#FFFFFF').grid(row=10, column=0, sticky=tk.W, pady=5)
        manufacturer_var = tk.StringVar()
        manufacturers = [''] + [mf['name'] for mf in service.manufacturers] \
            if service.manufacturers else ['', '暂无厂家']
        mf_menu = ttk.Combobox(form_frame, textvariable=manufacturer_var,
                              values=manufacturers[1:], font=('SimHei', 12),
                              width=23, state='normal')
        mf_menu.grid(row=10, column=1, pady=5)
        
        # 入库数量
        tk.Label(form_frame, text='入库数量：', font=('SimHei', 12),
                bg='#FFFFFF').grid(row=11, column=0, sticky=tk.W, pady=5)
        quantity_var = tk.StringVar()
        quantity_entry = tk.Entry(form_frame, textvariable=quantity_var,
                                font=('SimHei', 12), width=25)
        quantity_entry.grid(row=11, column=1, pady=5)
        
        # 批次号
        tk.Label(form_frame, text='批次号：', font=('SimHei', 12),
                bg='#FFFFFF').grid(row=12, column=0, sticky=tk.W, pady=5)
        batch_var = tk.StringVar()
        batch_entry = tk.Entry(form_frame, textvariable=batch_var,
                              font=('SimHei', 12), width=25)
        batch_entry.grid(row=12, column=1, pady=5)
        
        # 疫苗存储温度（输入框 + ℃ 图标）
        tk.Label(form_frame, text='疫苗存储温度：', font=('SimHei', 12),
                bg='#FFFFFF').grid(row=13, column=0, sticky=tk.W, pady=5)
        
        temp_input_frame = tk.Frame(form_frame, bg='#FFFFFF')
        temp_input_frame.grid(row=13, column=1, pady=5)
        
        vaccine_temp_var = tk.StringVar(value='2-8')  # 默认值（不含℃符号）
        
        temp_entry = tk.Entry(temp_input_frame, textvariable=vaccine_temp_var,
                             font=('SimHei', 12), width=18)
        temp_entry.pack(side=tk.LEFT)
        
        # 右侧显示摄氏度图标
        celsius_label = tk.Label(temp_input_frame, text='℃',
                                font=('SimHei', 14, 'bold'), fg='#333', bg='#FFFFFF')
        celsius_label.pack(side=tk.LEFT, padx=(2, 0))
        
        # 温度提示信息
        temp_hint = tk.Label(form_frame, 
                            text='示例：2-8、-20、-70 或 输入温度范围',
                            font=('SimHei', 9), fg='#999', bg='#FFFFFF')
        temp_hint.grid(row=13, column=2, sticky=tk.W, padx=10)
        
        # 库位（推荐库位）
        tk.Label(form_frame, text='推荐库位：', font=('SimHei', 12),
                bg='#FFFFFF').grid(row=14, column=0, sticky=tk.W, pady=5)
        storage_var = tk.StringVar()
        
        storage_combo = ttk.Combobox(form_frame, textvariable=storage_var,
                                   font=('SimHei', 12), width=23, state='readonly')
        storage_combo.grid(row=14, column=1, pady=5)
        
        # 温区映射：根据输入温度判断温区类型
        def get_temp_zone(temp_str):
            # 根据温度字符串判断温区
            if not temp_str:
                return ('refrigerator', '冷藏(2-8℃)')  # 默认冷藏
            
            temp_lower = temp_str.strip().lower()
            
            # 直接匹配关键词（包含中文和英文）
            if '超低温' in temp_str or 'ultra' in temp_lower:
                return ('ultra_low', '超低温(-70℃)')
            elif '冷冻' in temp_str or 'freezer' in temp_lower:
                return ('freezer', '冷冻(-20℃±5℃)')
            elif '冷藏' in temp_str or 'refrigerator' in temp_lower:
                return ('refrigerator', '冷藏(2-8℃)')
            
            # 提取温度数值进行智能判断
            import re
            numbers = re.findall(r'-?\d+', temp_str)
            
            if len(numbers) >= 1:
                try:
                    # 获取第一个数字作为主要温度值
                    main_temp = int(numbers[0])
                    
                    # 根据温度范围判断温区
                    if main_temp <= -50:  # -70等超低温
                        return ('ultra_low', f'超低温({temp_str}℃)')
                    elif main_temp <= -10:  # -15到-25等冷冻范围（包括-20）
                        return ('freezer', f'冷冻(-20℃±5℃或{temp_str}℃)')
                    elif main_temp <= 15:  # 0到15度范围，通常是冷藏（2-8℃）
                        return ('refrigerator', f'冷藏({temp_str}℃或2-8℃)')
                    else:  # 其他正数温度也归为冷藏
                        return ('refrigerator', f'冷藏({temp_str}℃)')
                        
                except (ValueError, TypeError):
                    pass
            
            # 默认返回冷藏
            return ('refrigerator', f'{temp_str}℃或冷藏(2-8℃)')
        
        def update_storage_options(show_warning=True):
            """根据输入的存储温度更新可用库位下拉列表"""
            temp_input = vaccine_temp_var.get()
            required_type, temp_desc = get_temp_zone(temp_input)

            # 确保冷库数据已加载（防止数据未初始化）
            if not service.cold_storages:
                # 尝试重新加载数据
                service.cold_storages = service.repository.load_cold_storage()
            
            available = []
            
            # 遍历所有冷库进行匹配
            for s in (service.cold_storages or []):
                storage_type = s.get('type', '')
                status = s.get('status', '')
                capacity = s.get('capacity', 0)
                used = s.get('used', 0)
                
                # 匹配条件：状态不是满的 + 类型匹配
                if status != 'full' and storage_type == required_type:
                    remaining = capacity - used
                    if remaining > 0 or used == 0:
                        available.append((s, remaining))

            # 按剩余容量降序排序
            available.sort(key=lambda x: x[1], reverse=True)

            # 构建选项列表
            options = [f"{s['id']} - {s['name']} [{s.get('temp_range', s.get('type', ''))}]" 
                      for s, _ in available]
            storage_combo['values'] = options

            if options:
                storage_combo.current(0)
            else:
                storage_var.set('')
                if show_warning:
                    messagebox.showwarning('无可用库位', f'{temp_desc} 温区暂无可用的库位！')
        
        def recommend_storage():
            """智能推荐最佳库位"""
            temp_input = vaccine_temp_var.get()
            required_type, temp_desc = get_temp_zone(temp_input)
            
            update_storage_options(show_warning=False)
            
            if storage_var.get():
                messagebox.showinfo('推荐成功', 
                    f'已为您推荐{temp_desc}温区最合适的库位：\n\n'
                    f'{storage_var.get()}\n\n'
                    f'💡 温度范围说明：\n'
                    f'• 冷藏(2-8℃)：适用于常规疫苗\n'
                    f'• 冷冻(-20℃±5℃)：适用于部分特殊疫苗\n'
                    f'• 超低温(-70℃)：适用于mRNA疫苗等')
            else:
                messagebox.showwarning('推荐失败', 
                    f'{temp_desc}温区暂无可用库位！\n\n'
                    f'请检查冷库配置或联系管理员添加{temp_desc}类型的冷库。\n\n'
                    f'当前可用冷库类型：冷藏、冷冻(-20℃±5℃)、超低温(-70℃)')
        
        # 绑定温度输入框变化事件（输入时实时更新，但不弹警告）
        vaccine_temp_var.trace_add('write', lambda *args: update_storage_options(show_warning=False))
        
        # 初始化库位列表（不显示警告）
        update_storage_options(show_warning=False)
        
        recommend_btn = tk.Button(form_frame, text='智能推荐库位',
                                command=recommend_storage, font=('SimHei', 11),
                                bg='#1E90FF', fg='white', width=15)
        recommend_btn.grid(row=14, column=2, pady=5, padx=10)
        
        # 备注
        tk.Label(form_frame, text='备注（存储条件）：', font=('SimHei', 12),
                bg='#FFFFFF').grid(row=15, column=0, sticky=tk.W, pady=5)
        remark_var = tk.StringVar(value='避光保存，不可倒置')
        remark_entry = tk.Entry(form_frame, textvariable=remark_var,
                              font=('SimHei', 12), width=40)
        remark_entry.grid(row=15, column=1, columnspan=2, pady=5)
        
        # 关键词按钮区
        keyword_frame = tk.Frame(form_frame, bg='#FFFFFF')
        keyword_frame.grid(row=16, column=0, columnspan=3, pady=10)
        
        keywords = STORAGE_KEYWORDS
        
        def add_keyword(keyword):
            current = remark_var.get()
            if keyword not in current:
                if current:
                    remark_var.set(current + '，' + keyword)
                else:
                    remark_var.set(keyword)
        
        for i, kw in enumerate(keywords):
            btn = tk.Button(keyword_frame, text=kw,
                          command=lambda k=kw: add_keyword(k),
                          font=('SimHei', 11), bg='#E8E8E8', fg='#333', width=10)
            btn.grid(row=i//5, column=i%5, padx=5, pady=2)
        
        # 提交按钮
        def submit():
            vaccine_id = id_var.get()
            name = name_var.get()
            category = category_var.get()
            prod_date = prod_date_var.get()
            expiry_date = expiry_date_var.get()
            manufacturer = manufacturer_var.get()
            quantity = quantity_var.get()
            batch_number = batch_var.get()
            
            # 获取存储温度（转换为标准格式）
            temp_input = vaccine_temp_var.get()
            _, temp_desc = get_temp_zone(temp_input)
            vaccine_type = temp_input if temp_input else '2-8℃'  # 使用用户输入的原始值
            
            storage_id = storage_var.get().split(' - ')[0] if ' - ' in storage_var.get() else storage_var.get()
            remark = remark_var.get()
            
            if not vaccine_id or not name or not quantity:
                messagebox.showerror('错误', '请填写必填项')
                return
            
            # 批号唯一性校验
            existing_vaccine = None
            for v in service.vaccines:
                if (v.get('batch_number') == batch_number and
                    v.get('name') == name and
                    v.get('category') == category and
                    v.get('manufacturer') == manufacturer and
                    v.get('expiry_date') == expiry_date and
                    v.get('status') == 'pending'):
                    existing_vaccine = v
                    break
            
            if existing_vaccine:
                existing_vaccine['quantity'] = existing_vaccine.get('quantity', 0) + int(quantity)
                existing_vaccine['stock_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if '入库单号' not in existing_vaccine or not existing_vaccine['入库单号']:
                    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                    existing_vaccine['入库单号'] = f'RK{current_time}{vaccine_id}'
                messagebox.showinfo('成功', f'疫苗批号{batch_number}已存在，已更新数量')
            else:
                current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                new_vaccine = {
                    'id': vaccine_id,
                    'name': name,
                    'category': category,
                    'production_date': prod_date,
                    'expiry_date': expiry_date,
                    'manufacturer': manufacturer,
                    'quantity': int(quantity),
                    'batch_number': batch_number,
                    'stock_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'pending',
                    'vaccine_type': vaccine_type,
                    'storage_id': storage_id,
                    'remark': remark,
                    '入库单号': f'RK{current_time}{vaccine_id}'
                }
                service.vaccines.append(new_vaccine)
                service.id_counter = max(service.id_counter, int(vaccine_id) + 1)
                messagebox.showinfo('成功', '疫苗入库登记成功，等待审核')
            
            service.save_data()
            
            action = f"添加疫苗入库：{name}（{batch_number}）-{quantity}剂"
            service.log_operation(action)
            
            # 清空表单
            id_var.set('')
            name_var.set('')
            quantity_var.set('')
            batch_var.set('')
        
        submit_btn = tk.Button(form_frame, text='提交入库',
                             command=submit, font=('SimHei', 14),
                             bg='#FF9900', fg='white', width=20)
        submit_btn.grid(row=17, column=0, columnspan=3, pady=20)
    
    # 调用内部函数渲染页面
    show_single_inventory_form()


def render_batch_inventory(parent, service):
    # 批量疫苗入库登记

    title = tk.Label(parent, text='批量疫苗入库登记',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)
    
    form_frame = tk.Frame(parent, bg='#FFFFFF', padx=40)
    form_frame.pack(pady=10, fill=tk.X)
    
    # 文件选择
    tk.Label(form_frame, text='选择CSV文件：', font=('SimHei', 12),
            bg='#FFFFFF').pack(anchor=tk.W, pady=10)
    
    file_path_var = tk.StringVar()
    file_entry = tk.Entry(form_frame, textvariable=file_path_var,
                         font=('SimHei', 12), width=50)
    file_entry.pack(pady=5, fill=tk.X)
    
    def browse_file():
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        file_path_var.set(file_path)
    
    browse_btn = tk.Button(form_frame, text='浏览文件', command=browse_file,
                         font=('SimHei', 12), bg='#1E90FF', fg='white', width=15)
    browse_btn.pack(pady=5, anchor=tk.W)
    
    # CSV格式说明
    tk.Label(form_frame, text='CSV文件格式：疫苗编号,疫苗名称,类别,生产日期,有效期至,生产厂家,数量,批号,疫苗类型,库位,备注',
            font=('SimHei', 10), bg='#FFFFFF', fg='#999').pack(anchor=tk.W, pady=10)
    
    # 示例数据区域
    sample_frame = tk.LabelFrame(form_frame, text='示例数据',
                               font=('SimHei', 11), bg='#F5F5F5')
    sample_frame.pack(pady=10, fill=tk.X)
    sample_text = """V001,流感疫苗,灭活疫苗（死疫苗）,2026-01-01,2026-12-31,北京科兴,100,B2026001,冷藏,冰箱1,
V002,新冠疫苗,灭活疫苗（死疫苗）,2026-02-01,2026-11-30,国药集团,200,B2026002,冷藏,冰箱2,避光保存"""
    sample_label = tk.Label(sample_frame, text=sample_text, font=('SimHei', 10),
                           bg='#F5F5F5', fg='#666', justify=tk.LEFT)
    sample_label.pack(pady=10, padx=10)
    
    def import_data():
        file_path = file_path_var.get()
        if not file_path:
            messagebox.showerror('错误', '请选择文件')
            return
        
        if not file_path.endswith('.csv'):
            messagebox.showerror('错误', '请选择CSV格式文件')
            return
        
        result = service.batch_add_vaccines(file_path)
        messagebox.showinfo('导入结果', result)
    
    import_btn = tk.Button(form_frame, text='开始导入', command=import_data,
                         font=('SimHei', 14), bg='#FF9900', fg='white', width=20)
    import_btn.pack(pady=20)


def render_inventory_audit(parent, service):
    # 疫苗入库审核

    title = tk.Label(parent, text='疫苗入库审核',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)
    
    pending_vaccines = [v for v in service.vaccines if v.get('status') == 'pending']
    
    if not pending_vaccines:
        tk.Label(parent, text='暂无待审核的疫苗入库记录',
                font=('SimHei', 14), bg='#FFFFFF').pack(pady=20)
        return
    
    list_frame = tk.Frame(parent, bg='#FFFFFF', padx=40)
    list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    
    for vaccine in pending_vaccines:
        item_frame = tk.Frame(list_frame, bg='#F5F5F5', bd=1, relief=tk.SUNKEN)
        item_frame.pack(fill=tk.X, pady=5, padx=10)
        
        info_frame = tk.Frame(item_frame, bg='#F5F5F5')
        info_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(info_frame,
                text=f"编号: {vaccine['id']} | 名称: {vaccine['name']} | 批次: {vaccine.get('batch_number', '-')} | 数量: {vaccine['quantity']}剂 | 有效期: {vaccine['expiry_date']}",
                font=('SimHei', 12), bg='#F5F5F5').pack(anchor=tk.W)
        
        def approve(vid=vaccine['id']):
            for v in service.vaccines:
                if v['id'] == vid:
                    v['status'] = 'in_stock'
                    v['audit_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    service.save_data()
                    messagebox.showinfo('成功', '审核通过')
                    break
        
        def reject(vid=vaccine['id']):
            for v in service.vaccines:
                if v['id'] == vid:
                    v['status'] = 'rejected'
                    service.save_data()
                    messagebox.showinfo('成功', '已拒绝')
                    break
        
        btn_frame = tk.Frame(item_frame, bg='#F5F5F5')
        btn_frame.pack(pady=5, padx=20, anchor=tk.E)
        
        approve_btn = tk.Button(btn_frame, text='通过', command=approve,
                              font=('SimHei', 11), bg='#00CC00', fg='white', width=10)
        approve_btn.pack(side=tk.RIGHT, padx=5)
        
        reject_btn = tk.Button(btn_frame, text='拒绝', command=reject,
                             font=('SimHei', 11), bg='#FF6347', fg='white', width=10)
        reject_btn.pack(side=tk.RIGHT)


def render_inventory_doc(parent, service):
    # 入库单据管理

    from tkinter import ttk

    # 标题
    title = tk.Label(parent, text='📋 入库单据管理',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=(15, 10))

    # ==================== 左右分栏主容器 ====================
    main_container = tk.Frame(parent, bg='#FFFFFF')
    main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
    
    # 配置网格布局权重
    main_container.columnconfigure(0, weight=6)   # 左侧60%
    main_container.columnconfigure(1, weight=4)   # 右侧40%
    main_container.rowconfigure(1, weight=1)

    # ==================== 左侧面板（数据列表）====================
    left_panel = tk.Frame(main_container, bg='#FFFFFF')
    left_panel.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=(0, 10))

    # 查询条件区域
    filter_frame = tk.LabelFrame(left_panel, text='🔍 查询条件', font=('SimHei', 10),
                                bg='#F5F8FA', padx=12, pady=8)
    filter_frame.pack(fill=tk.X, pady=(0, 8))
    
    # 第一行：批次号 + 疫苗名称
    row1 = tk.Frame(filter_frame, bg='#F5F8FA')
    row1.pack(fill=tk.X, pady=3)
    
    tk.Label(row1, text='批次号/单据号：', font=('SimHei', 9), bg='#F5F8FA').pack(side=tk.LEFT)
    doc_id_var = tk.StringVar()
    tk.Entry(row1, textvariable=doc_id_var, font=('SimHei', 9), width=14).pack(side=tk.LEFT, padx=(0, 10))
    
    tk.Label(row1, text='疫苗名称：', font=('SimHei', 9), bg='#F5F8FA').pack(side=tk.LEFT)
    vaccine_names = list(set(v.get('name', '') for v in (service.vaccines or []) if v.get('name')))
    vaccine_name_var = tk.StringVar()
    vaccine_combo = ttk.Combobox(row1, textvariable=vaccine_name_var,
                                values=[''] + vaccine_names[:20], font=('SimHei', 9), width=12,
                                state='readonly')
    vaccine_combo.pack(side=tk.LEFT)

    # 第二行：日期范围 + 查询按钮
    row2 = tk.Frame(filter_frame, bg='#F5F8FA')
    row2.pack(fill=tk.X, pady=3)
    
    tk.Label(row2, text='日期范围：', font=('SimHei', 9), bg='#F5F8FA').pack(side=tk.LEFT)
    start_date_var = tk.StringVar()
    tk.Entry(row2, textvariable=start_date_var, font=('SimHei', 9), width=10).pack(side=tk.LEFT, padx=(0, 2))
    tk.Label(row2, text='至', font=('SimHei', 9), bg='#F5F8FA').pack(side=tk.LEFT)
    end_date_var = tk.StringVar()
    tk.Entry(row2, textvariable=end_date_var, font=('SimHei', 9), width=10).pack(side=tk.LEFT, padx=(2, 10))

    search_btn = tk.Button(row2, text='查询', command=lambda: search_documents(),
                          font=('SimHei', 9), bg='#1E90FF', fg='white', width=6)
    search_btn.pack(side=tk.LEFT)

    # 结果统计
    result_label = tk.Label(left_panel, text='', font=('SimHei', 9), fg='#666', bg='#FFFFFF')
    result_label.pack(anchor=tk.W, pady=(2, 5))

    # 表格容器（带滚动条）
    table_container = tk.Frame(left_panel, bg='#E8E8E8', relief=tk.SUNKEN, bd=1)
    table_container.pack(fill=tk.BOTH, expand=True)

    # 创建Canvas和滚动条
    table_canvas = tk.Canvas(table_container, bg='#FFFFFF', highlightthickness=0)
    scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=table_canvas.yview)
    
    left_scroll_frame = tk.Frame(table_canvas, bg='#FFFFFF')
    left_scroll_frame.bind("<Configure>", lambda e: table_canvas.configure(scrollregion=table_canvas.bbox("all")))
    
    table_canvas.create_window((0, 0), window=left_scroll_frame, anchor="nw")
    table_canvas.configure(yscrollcommand=scrollbar.set)
    
    # 绑定鼠标滚轮
    def on_mousewheel(event):
        table_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    table_canvas.bind_all("<MouseWheel>", on_mousewheel)

    # 布局
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    table_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 表头
    header_frame = tk.Frame(left_scroll_frame, bg='#2C3E50')
    header_frame.pack(fill=tk.X)

    headers = ['批次号/单据号', '入库时间', '疫苗名称', '厂家', '数量', '状态', '操作']
    header_widths = [14, 10, 14, 10, 6, 7, 6]

    for h, w in zip(headers, header_widths):
        tk.Label(header_frame, text=h, font=('SimHei', 9, 'bold'),
                fg='white', bg='#2C3E50', width=w).pack(side=tk.LEFT, padx=1, pady=4)

    # 数据显示区域
    data_frame = tk.Frame(left_scroll_frame, bg='#FFFFFF')
    data_frame.pack(fill=tk.X)

    # ==================== 右侧面板（详情展示）====================
    right_panel = tk.Frame(main_container, bg='#F8F9FA', relief=tk.GROOVE, bd=2)
    right_panel.grid(row=0, column=1, rowspan=2, sticky='nsew')

    # 详情标题
    detail_header = tk.Frame(right_panel, bg='#2C3E50')
    detail_header.pack(fill=tk.X)
    
    tk.Label(detail_header, text='📄 单据详情', 
             font=('SimHei', 12, 'bold'), fg='white', bg='#2C3E50').pack(pady=10)

    # 详情内容区（可滚动）
    detail_container = tk.Frame(right_panel, bg='#F8F9FA')
    detail_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    
    # 默认提示
    default_hint = tk.Label(detail_container,
                            text='💡 点击左侧表格的"查看"按钮\n\n在此处显示单据详细信息',
                            font=('SimHei', 11), fg='#999', bg='#F8F9FA',
                            justify=tk.CENTER)
    default_hint.pack(expand=True)

    # 详情信息变量
    detail_widgets = {}

    # 状态映射
    status_map = {
        'in_stock': ('在库', '#00CC00'),
        'pending': ('待审核', '#FF9900'),
        'rejected': ('已驳回', '#FF6347'),
        'expired': ('已过期', '#999'),
        'out_stock': ('全出库', '#FF6347')
    }

    def get_status_text(status):
        """状态文字转换"""
        text, _color = status_map.get(status, (status, '#333'))
        return text

    def show_detail_in_right_panel(doc):
        """在右侧面板显示单据详情（不使用弹窗）"""
        
        # 清除旧内容
        for widget in detail_container.winfo_children():
            widget.destroy()
            
        detail_widgets.clear()

        # 详情标题栏
        title_bar = tk.Frame(detail_container, bg='#1E90FF')
        title_bar.pack(fill=tk.X, pady=(0, 15))
        
        batch_or_doc = str(doc.get('batch_number', '') or doc.get('入库单号', '未分配'))
        tk.Label(title_bar, text=f"📋 {batch_or_doc}", 
                 font=('SimHei', 14, 'bold'), fg='white', bg='#1E90FF').pack(pady=10)

        # 信息卡片
        info_card = tk.Frame(detail_container, bg='#FFFFFF', relief=tk.RAISED, bd=1)
        info_card.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 详细信息字段
        details = [
            ('🏷️ 单据号', doc.get('入库单号', '未生成')),
            ('💉 疫苗名称', doc.get('name', '-')),
            ('📂 疫苗类别', doc.get('category', '-')),
            ('🏭 生产厂家', doc.get('manufacturer', '-')),
            ('📦 批次号', doc.get('batch_number', '-')),
            ('📊 数量', f"{doc.get('quantity', 0)} 剂"),
            ('📅 生产日期', doc.get('production_date', '-')),
            ('⏰ 有效期至', doc.get('expiry_date', '-')),
            ('🕐 入库时间', doc.get('入库时间', doc.get('stock_time', '-'))),
            ('✅ 审核状态', get_status_text(doc.get('status', '-'))),
            ('🌡️ 存储类型', doc.get('vaccine_type', doc.get('存储温度', '-'))),
            ('📍 库位编号', doc.get('storage_id', '待分配')),
            ('📝 备注信息', doc.get('remark', '无') or '无'),
        ]

        for i, (label, value) in enumerate(details):
            # 字段行框架
            field_row = tk.Frame(info_card, bg='#FFFFFF')
            field_row.pack(fill=tk.X, padx=12, pady=4)
            
            # 标签
            lbl = tk.Label(field_row, text=label, font=('SimHei', 10),
                         fg='#555', bg='#FFFFFF', anchor='e', width=12)
            lbl.pack(side=tk.LEFT)
            
            # 值（根据类型设置颜色）
            color = '#333'
            if label == '✅ 审核状态':
                if value in ['已驳回', 'rejected']:
                    color = '#FF6347'
                elif value == '已审核' or value == 'in_stock':
                    color = '#00CC00'
                elif value == '待审核' or value == 'pending':
                    color = '#FF9900'
            elif label == '⏰ 有效期至':
                # 检查是否即将过期或已过期
                try:
                    expiry = datetime.datetime.strptime(value, '%Y-%m-%d').date() if value and value != '-' else None
                    if expiry:
                        days_left = (expiry - datetime.date.today()).days
                        if days_left < 0:
                            color = '#FF0000'
                        elif days_left <= 30:
                            color = '#FF9900'
                        else:
                            color = '#00CC00'
                except (ValueError, TypeError):
                    pass
            
            val_lbl = tk.Label(field_row, text=str(value)[:30], font=('SimHei', 10, 'bold'),
                              fg=color, bg='#FFFFFF', anchor='w', wraplength=250)
            val_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
            
            detail_widgets[label] = val_lbl

        # 操作按钮区
        action_frame = tk.Frame(detail_container, bg='#F8F9FA')
        action_frame.pack(fill=tk.X, pady=10)
        
        # 关闭按钮
        close_btn = tk.Button(action_frame, text='收起详情', 
                             command=lambda: clear_detail_panel(),
                             font=('SimHei', 10), bg='#999999', fg='white', width=12)
        close_btn.pack(pady=5)

    def clear_detail_panel():
        """清除右侧详情面板，恢复默认提示"""
        for widget in detail_container.winfo_children():
            widget.destroy()
        detail_widgets.clear()
        
        default_hint = tk.Label(detail_container,
                                text='💡 点击左侧表格的"查看"按钮\n\n在此处显示单据详细信息',
                                font=('SimHei', 11), fg='#999', bg='#F8F9FA',
                                justify=tk.CENTER)
        default_hint.pack(expand=True)

    def refresh_table(data_list):
        """刷新表格数据"""
        # 清除旧数据
        for widget in data_frame.winfo_children():
            widget.destroy()

        if not data_list:
            empty_label = tk.Label(data_frame, text='暂无符合条件的记录',
                                  font=('SimHei', 11), fg='#999', bg='#FFFFFF')
            empty_label.pack(pady=30)
            return

        # 显示前25条数据
        display_data = data_list[:25]
        
        for idx, doc in enumerate(display_data):
            bg_color = '#F5F5F5' if idx % 2 == 0 else '#FFFFFF'
            row = tk.Frame(data_frame, bg=bg_color)
            row.pack(fill=tk.X)

            # 批次号/单据号（优先显示批次号）
            batch_or_doc = str(doc.get('batch_number', '') or doc.get('入库单号', '-'))
            
            values = [
                batch_or_doc[:13],  # 批次号或单据号
                str(doc.get('入库时间') or doc.get('stock_time', '-'))[:10],
                str(doc.get('name', '-'))[:12],
                str(doc.get('manufacturer', '-'))[:9],
                f"{doc.get('quantity', 0)}",
            ]

            for val, w in zip(values, header_widths[:-2]):
                tk.Label(row, text=val, font=('SimHei', 8),
                        fg='#333', bg=bg_color, width=w).pack(side=tk.LEFT, padx=1, pady=3)
            
            # 状态标签（彩色）
            status = doc.get('status', '-')
            status_text, status_color = status_map.get(status, (status, '#333'))
            tk.Label(row, text=status_text, font=('SimHei', 8, 'bold'),
                    fg=status_color, bg=bg_color, width=header_widths[-2]).pack(side=tk.LEFT, padx=1, pady=3)

            # 查看按钮（点击后在右侧显示详情）
            btn = tk.Button(row, text='查看', font=('SimHei', 8),
                           bg='#1E90FF', fg='white', bd=0, width=6,
                           cursor='hand2',
                           command=lambda d=doc: show_detail_in_right_panel(d))
            btn.pack(side=tk.LEFT, padx=1, pady=3)
            
            # 鼠标悬停效果
            def on_enter(e, r=row):
                r.config(bg='#E3F2FD')
            def on_leave(e, r=row):
                r.config(bg=bg_color)
            
            row.bind('<Enter>', lambda e, r=row: on_enter(e, r))
            row.bind('<Leave>', lambda e, r=row: on_leave(e, r))

        result_label.config(text=f'共 {len(data_list)} 条记录（显示前 {min(len(display_data), 25)} 条）')

    def search_documents():
        """执行查询 - 支持按批次号/入库单号搜索"""
        search_id = doc_id_var.get().strip()  # 可以是批次号或入库单号
        vname = vaccine_name_var.get()
        start = start_date_var.get().strip()
        end = end_date_var.get().strip()

        results = []
        for v in (service.vaccines or []):
            # 只显示已审核或在库的疫苗（有完整入库记录的）
            if not (v.get('status') in ['in_stock', 'pending', 'rejected'] or 
                   v.get('入库单号') or v.get('batch_number')):
                continue

            match = True
            
            # 支持按批次号或入库单号搜索（两者都匹配）
            if search_id:
                batch_match = search_id in str(v.get('batch_number', ''))
                doc_match = search_id in str(v.get('入库单号', ''))
                if not (batch_match or doc_match):
                    match = False
                    
            if vname and v.get('name') != vname:
                match = False
            if start:
                stock_time = v.get('入库时间', v.get('stock_time', ''))
                if stock_time and stock_time < start:
                    match = False
            if end:
                stock_time = v.get('入库时间', v.get('stock_time', ''))
                if stock_time and stock_time > end + ' 23:59:59':
                    match = False

            if match:
                results.append(v)

        refresh_table(results)

    # 初始加载所有数据
    search_documents()


# 导出别名供路由器使用
render_single_inventory = render_single_inventory
render_batch_inventory = render_batch_inventory
render_inventory_audit = render_inventory_audit
render_inventory_doc = render_inventory_doc


def render_inventory_record(parent, service):
    # 入库记录

    title = tk.Label(parent, text='入库记录',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)

    # 筛选条件区域
    filter_frame = tk.LabelFrame(parent, text='筛选条件', font=('SimHei', 11),
                                bg='#F5F5F5', padx=15, pady=10)
    filter_frame.pack(fill=tk.X, padx=40, pady=(0, 15))

    # 第一行：疫苗名称 + 批次号
    row1 = tk.Frame(filter_frame, bg='#F5F5F5')
    row1.pack(fill=tk.X, pady=5)

    tk.Label(row1, text='疫苗名称：', font=('SimHei', 11), bg='#F5F5F5').pack(side=tk.LEFT)
    vaccine_names = list(set(v.get('name', '') for v in service.vaccines if v.get('name')))
    vaccine_name_var = tk.StringVar()
    from tkinter import ttk
    vaccine_combo = ttk.Combobox(row1, textvariable=vaccine_name_var,
                                values=[''] + vaccine_names, font=('SimHei', 11), width=16,
                                state='readonly')
    vaccine_combo.pack(side=tk.LEFT, padx=(0, 20))

    tk.Label(row1, text='批次号：', font=('SimHei', 11), bg='#F5F5F5').pack(side=tk.LEFT)
    batch_var = tk.StringVar()
    tk.Entry(row1, textvariable=batch_var, font=('SimHei', 11), width=14).pack(side=tk.LEFT)

    # 第二行：日期范围 + 查询按钮
    row2 = tk.Frame(filter_frame, bg='#F5F5F5')
    row2.pack(fill=tk.X, pady=5)

    tk.Label(row2, text='日期范围：', font=('SimHei', 11), bg='#F5F5F5').pack(side=tk.LEFT)
    start_date_var = tk.StringVar()
    tk.Entry(row2, textvariable=start_date_var, font=('SimHei', 11), width=12).pack(side=tk.LEFT, padx=(0, 5))
    tk.Label(row2, text='至', font=('SimHei', 11), bg='#F5F5F5').pack(side=tk.LEFT)
    end_date_var = tk.StringVar()
    tk.Entry(row2, textvariable=end_date_var, font=('SimHei', 11), width=12).pack(side=tk.LEFT, padx=(5, 20))

    search_btn = tk.Button(row2, text='🔍 查询', command=lambda: search_records(),
                          font=('SimHei', 11), bg='#1E90FF', fg='white', bd=0, width=10)
    search_btn.pack(side=tk.LEFT)

    # 结果统计标签
    result_label = tk.Label(parent, text='', font=('SimHei', 10), fg='#666', bg='#FFFFFF')
    result_label.pack(anchor=tk.W, padx=40)

    # 表格容器（带滚动条）
    table_container = tk.Frame(parent, bg='#FFFFFF')
    table_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 15))

    canvas = tk.Canvas(table_container, bg='#FFFFFF', highlightthickness=0)
    scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#FFFFFF')

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # 表头
    header_frame = tk.Frame(scrollable_frame, bg='#2C3E50')
    header_frame.pack(fill=tk.X)

    headers = ['单号', '疫苗名', '批次号', '数量', '入库日期', '状态']
    header_widths = [14, 14, 10, 6, 12, 10]

    for h, w in zip(headers, header_widths):
        tk.Label(header_frame, text=h, font=('SimHei', 11, 'bold'),
                fg='white', bg='#2C3E50', width=w).pack(side=tk.LEFT, padx=1, pady=6)

    # 数据显示区域
    data_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
    data_frame.pack(fill=tk.X)

    def get_status_color(status):
        """根据状态返回颜色"""
        if status in ['in_stock', '已审核']:
            return '#00CC00'  # 绿色 - 已审核/在库
        elif status == 'pending':
            return '#FF9900'  # 橙色 - 待审核
        elif status in ['rejected', 'expired', 'out_stock']:
            return '#FF6347'  # 红色 - 已驳回/过期/出库
        return '#333'

    def get_status_text(status):
        """状态文字转换"""
        status_map = {
            'pending': '待审核',
            'in_stock': '在库',
            'rejected': '已驳回',
            'expired': '已过期',
            'out_stock': '全出库'
        }
        return status_map.get(status, status)

    # 行悬停效果
    def on_row_enter(e, r, vals, stat, s_color, bg_orig):
        hover_bg = '#E3F2FD'
        r.configure(bg=hover_bg)
        for child in r.winfo_children():
            try:
                child.configure(bg=hover_bg)
            except tk.TclError:
                pass

    def on_row_leave(e, r, vals, stat, s_color, bg_orig):
        r.configure(bg=bg_orig)
        for idx, child in enumerate(r.winfo_children()):
            try:
                if idx == len(r.winfo_children()) - 1:
                    child.configure(bg=bg_orig, fg=s_color)
                else:
                    child.configure(bg=bg_orig, fg='#333')
            except tk.TclError:
                pass

    def refresh_table(data_list):
        """刷新表格数据"""
        for widget in data_frame.winfo_children():
            widget.destroy()

        if not data_list:
            empty_label = tk.Label(data_frame, text='暂无符合条件的记录',
                                  font=('SimHei', 12), fg='#999', bg='#FFFFFF')
            empty_label.pack(pady=30)
            return

        display_data = data_list[:20]
        for idx, record in enumerate(display_data):
            bg_color = '#F9F9F9' if idx % 2 == 0 else '#FFFFFF'
            row = tk.Frame(data_frame, bg=bg_color)
            row.pack(fill=tk.X)

            status = record.get('status', '-')
            status_text = get_status_text(status)
            status_color = get_status_color(status)

            values = [
                str(record.get('入库单号', '-'))[:12],
                str(record.get('name', '-'))[:12],
                str(record.get('batch_number', '-'))[:8],
                f"{record.get('quantity', 0)}",
                str(record.get('入库时间', record.get('stock_time', '-')))[:10],
            ]

            for val, w in zip(values, header_widths[:-1]):
                tk.Label(row, text=val, font=('SimHei', 10),
                        fg='#333', bg=bg_color, width=w).pack(side=tk.LEFT, padx=1, pady=4)

            # 状态标签（彩色）
            status_label = tk.Label(row, text=status_text, font=('SimHei', 10, 'bold'),
                                   fg=status_color, bg=bg_color, width=header_widths[-1])
            status_label.pack(side=tk.LEFT, padx=1, pady=4)

            # 行悬停高亮效果
            row.bind('<Enter>', lambda e, r=row, bg=bg_color: on_row_enter(e, r, None, None, None, bg))
            row.bind('<Leave>', lambda e, r=row, bg=bg_color: on_row_leave(e, r, None, None, status_color, bg))
            for child in row.winfo_children():
                child.bind('<Enter>', lambda e, r=row, bg=bg_color: on_row_enter(e, r, None, None, None, bg))
                child.bind('<Leave>', lambda e, r=row, bg=bg_color: on_row_leave(e, r, None, None, status_color, bg))

        result_label.config(text=f'共 {len(data_list)} 条记录（显示前 {min(len(display_data), 20)} 条）')

    def search_records():
        """执行查询 - 显示所有已入库的疫苗记录"""
        vname = vaccine_name_var.get()
        batch = batch_var.get().strip()
        start = start_date_var.get().strip()
        end = end_date_var.get().strip()

        results = []
        for v in service.vaccines:
            # 只显示已审核或在库的疫苗（有完整入库信息的）
            if v.get('status') not in ['in_stock', 'pending', 'rejected']:
                continue
                
            # 如果既没有入库单号也没有入库时间和批次号，跳过
            if not (v.get('入库单号') or v.get('入库时间') or v.get('batch_number')):
                continue
            
            match = True
            if vname and v.get('name') != vname:
                match = False
            if batch and batch not in str(v.get('batch_number', '')):
                match = False
            if start:
                stock_time = v.get('入库时间', v.get('stock_time', ''))
                if stock_time and stock_time < start:
                    match = False
            if end:
                stock_time = v.get('入库时间', v.get('stock_time', ''))
                if stock_time and stock_time > end + ' 23:59:59':
                    match = False

            if match:
                results.append(v)

        # 按入库时间倒序排序
        results.sort(key=lambda x: x.get('入库时间', x.get('stock_time', '')), reverse=True)

        refresh_table(results)

    # 初始加载所有数据
    search_records()

    # 绑定滚动事件
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


render_inventory_record = render_inventory_record
