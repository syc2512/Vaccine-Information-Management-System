# 疫苗信息相关页面

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import re


def render_vaccine_search(parent, service):
    """疫苗信息查询页面 - 左右分栏布局（左侧表格 + 右侧详情）"""
    
    from tkinter import ttk

    # 标题
    title = tk.Label(parent, text='💉 疫苗信息查询',
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
    
    # 第一行：疫苗名称 + 类别
    row1 = tk.Frame(filter_frame, bg='#F5F8FA')
    row1.pack(fill=tk.X, pady=3)
    
    tk.Label(row1, text='疫苗名称：', font=('SimHei', 9), bg='#F5F8FA').pack(side=tk.LEFT)
    name_var = tk.StringVar()
    tk.Entry(row1, textvariable=name_var, font=('SimHei', 9), width=14).pack(side=tk.LEFT, padx=(0, 12))
    
    tk.Label(row1, text='类别：', font=('SimHei', 9), bg='#F5F8FA').pack(side=tk.LEFT)
    categories = list(set(v.get('category', '') for v in (service.vaccines or []) if v.get('category')))
    category_var = tk.StringVar()
    category_combo = ttk.Combobox(row1, textvariable=category_var,
                                 values=[''] + categories[:20], font=('SimHei', 9), width=13,
                                 state='readonly')
    category_combo.pack(side=tk.LEFT)

    # 第二行：生产厂家 + 查询按钮
    row2 = tk.Frame(filter_frame, bg='#F5F8FA')
    row2.pack(fill=tk.X, pady=3)

    tk.Label(row2, text='生产厂家：', font=('SimHei', 9), bg='#F5F8FA').pack(side=tk.LEFT)
    manufacturers = [m['name'] for m in (service.manufacturers or []) if service.manufacturers] if hasattr(service, 'manufacturers') and service.manufacturers else []
    manufacturer_var = tk.StringVar()
    mfr_combo = ttk.Combobox(row2, textvariable=manufacturer_var,
                            values=[''] + manufacturers[:20], font=('SimHei', 9), width=13,
                            state='readonly')
    mfr_combo.pack(side=tk.LEFT, padx=(0, 12))

    search_btn = tk.Button(row2, text='查询', command=lambda: search_vaccines(),
                          font=('SimHei', 9), bg='#1E90FF', fg='white', bd=0, width=6)
    search_btn.pack(side=tk.LEFT)

    # 结果统计
    result_label = tk.Label(left_panel, text='', font=('SimHei', 9), fg='#666', bg='#FFFFFF')
    result_label.pack(anchor=tk.W, pady=(2, 5))

    # 表格容器（带滚动条）
    table_container = tk.Frame(left_panel, bg='#E8E8E8', relief=tk.SUNKEN, bd=1)
    table_container.pack(fill=tk.BOTH, expand=True)

    table_canvas = tk.Canvas(table_container, bg='#FFFFFF', highlightthickness=0)
    scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=table_canvas.yview)
    
    scrollable_frame = tk.Frame(table_canvas, bg='#FFFFFF')
    scrollable_frame.bind("<Configure>", lambda e: table_canvas.configure(scrollregion=table_canvas.bbox("all")))
    
    table_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    table_canvas.configure(yscrollcommand=scrollbar.set)
    
    # 鼠标滚轮事件
    def on_mousewheel(event):
        table_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    table_canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    table_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 表头
    header_frame = tk.Frame(scrollable_frame, bg='#2C3E50')
    header_frame.pack(fill=tk.X)

    headers = ['ID', '名称', '类别', '厂家', '有效期', '库存', '状态', '操作']
    header_widths = [5, 12, 14, 11, 10, 5, 7, 6]

    for h, w in zip(headers, header_widths):
        tk.Label(header_frame, text=h, font=('SimHei', 9, 'bold'),
                fg='white', bg='#2C3E50', width=w).pack(side=tk.LEFT, padx=1, pady=4)

    # 数据显示区域
    data_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
    data_frame.pack(fill=tk.X)

    # ==================== 右侧面板（详情展示）====================
    right_panel = tk.Frame(main_container, bg='#F8F9FA', relief=tk.GROOVE, bd=2)
    right_panel.grid(row=0, column=1, rowspan=2, sticky='nsew')

    # 详情标题
    detail_header = tk.Frame(right_panel, bg='#2C3E50')
    detail_header.pack(fill=tk.X)
    
    tk.Label(detail_header, text='💉 疫苗详情', 
             font=('SimHei', 12, 'bold'), fg='white', bg='#2C3E50').pack(pady=10)

    # 详情内容区
    detail_container = tk.Frame(right_panel, bg='#F8F9FA')
    detail_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    
    # 默认提示
    default_hint = tk.Label(detail_container,
                            text='💡 点击左侧表格的"查看"按钮\n\n在此处显示疫苗详细信息',
                            font=('SimHei', 11), fg='#999', bg='#F8F9FA',
                            justify=tk.CENTER)
    default_hint.pack(expand=True)
    
    def get_expiry_status(expiry_date):
        """根据有效期判断状态"""
        if not expiry_date:
            return ('未知', '#999999')

        try:
            today = datetime.date.today()
            expiry = datetime.datetime.strptime(expiry_date, '%Y-%m-%d').date()
            days_left = (expiry - today).days

            if days_left < 0:
                return ('已过期', '#FF6347')  # 红色
            elif days_left <= 30:
                return ('即将过期', '#FF9900')  # 橙色
            else:
                return ('正常', '#00CC00')  # 绿色
        except (ValueError, TypeError):
            return ('未知', '#999999')

    def show_detail_in_right_panel(vaccine):
        """在右侧面板显示疫苗详情（不使用弹窗）"""
        
        # 清除旧内容
        for widget in detail_container.winfo_children():
            widget.destroy()
            
        # 详情标题栏（显示疫苗名称）
        title_bar = tk.Frame(detail_container, bg='#1E90FF')
        title_bar.pack(fill=tk.X, pady=(0, 12))
        
        vac_name = vaccine.get('name', '未知疫苗')
        vac_id = str(vaccine.get('id', '-'))
        
        tk.Label(title_bar, text=f"💉 {vac_name}  (ID: {vac_id})", 
                 font=('SimHei', 13, 'bold'), fg='white', bg='#1E90FF').pack(pady=10)

        # 信息卡片
        info_card = tk.Frame(detail_container, bg='#FFFFFF', relief=tk.RAISED, bd=1)
        info_card.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 详细信息字段
        status_text, status_color = get_expiry_status(vaccine.get('expiry_date', ''))
        
        details = [
            ('🆔 ID编号', str(vaccine.get('id', '-'))),
            ('💉 疫苗名称', vaccine.get('name', '-')),
            ('📂 疫苗类别', vaccine.get('category', '-')),
            ('🏭 生产厂家', vaccine.get('manufacturer', '-')),
            ('📦 批次号', vaccine.get('batch_number', '-')),
            ('📅 生产日期', vaccine.get('production_date', '-')),
            ('⏰ 有效期至', vaccine.get('expiry_date', '-')),
            ('📊 库存数量', f"{vaccine.get('quantity', 0)} 剂"),
            ('🌡️ 存储类型', vaccine.get('vaccine_type', vaccine.get('存储温度', '-'))),
            ('📍 库位编号', vaccine.get('storage_id', '待分配')),
            ('📋 入库单号', str(vaccine.get('入库单号', '未生成'))),
            ('🕐 入库时间', vaccine.get('入库时间', vaccine.get('stock_time', '-'))),
            ('✅ 当前状态', f"{status_text} ({vaccine.get('status', '-')})"),
            ('📝 备注信息', vaccine.get('remark', '无') or '无'),
        ]

        for i, (label, value) in enumerate(details):
            field_row = tk.Frame(info_card, bg='#FFFFFF')
            field_row.pack(fill=tk.X, padx=10, pady=3)
            
            lbl = tk.Label(field_row, text=label, font=('SimHei', 9),
                         fg='#555', bg='#FFFFFF', anchor='e', width=11)
            lbl.pack(side=tk.LEFT)
            
            color = '#333'
            if label == '⏰ 有效期至':
                _, color = get_expiry_status(value)
            elif label == '✅ 当前状态':
                color = status_color
            
            val_lbl = tk.Label(field_row, text=str(value)[:28], font=('SimHei', 9, 'bold'),
                              fg=color, bg='#FFFFFF', anchor='w', wraplength=220)
            val_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

        # 操作按钮区
        action_frame = tk.Frame(detail_container, bg='#F8F9FA')
        action_frame.pack(fill=tk.X, pady=8)
        
        close_btn = tk.Button(action_frame, text='收起详情', 
                             command=lambda: clear_detail_panel(),
                             font=('SimHei', 10), bg='#999999', fg='white', width=12)
        close_btn.pack(pady=4)

    def clear_detail_panel():
        """清除右侧详情面板，恢复默认提示"""
        for widget in detail_container.winfo_children():
            widget.destroy()
        
        default_hint = tk.Label(detail_container,
                                text='💡 点击左侧表格的"查看"按钮\n\n在此处显示疫苗详细信息',
                                font=('SimHei', 11), fg='#999', bg='#F8F9FA',
                                justify=tk.CENTER)
        default_hint.pack(expand=True)

    def refresh_table(data_list):
        """刷新表格数据"""
        for widget in data_frame.winfo_children():
            widget.destroy()

        if not data_list:
            empty_label = tk.Label(data_frame, text='暂无符合条件的疫苗记录',
                                  font=('SimHei', 11), fg='#999', bg='#FFFFFF')
            empty_label.pack(pady=30)
            return

        display_data = data_list[:25]  # 显示25条
        
        for idx, vac in enumerate(display_data):
            bg_color = '#F5F5F5' if idx % 2 == 0 else '#FFFFFF'
            row = tk.Frame(data_frame, bg=bg_color)
            row.pack(fill=tk.X)

            values = [
                str(vac.get('id', '-'))[:4],
                str(vac.get('name', '-'))[:11],
                str(vac.get('category', '-'))[:12],
                str(vac.get('manufacturer', '-'))[:9],
                str(vac.get('expiry_date', '-'))[:10],
                f"{vac.get('quantity', 0)}"
            ]

            for val, w in zip(values, header_widths[:-2]):
                tk.Label(row, text=val, font=('SimHei', 8),
                        fg='#333', bg=bg_color, width=w).pack(side=tk.LEFT, padx=1, pady=3)

            # 状态标签（彩色）
            status_text, status_color = get_expiry_status(vac.get('expiry_date', ''))
            tk.Label(row, text=status_text, font=('SimHei', 8, 'bold'),
                    fg=status_color, bg=bg_color, width=header_widths[-2]).pack(side=tk.LEFT, padx=1, pady=3)

            # 查看按钮（点击后在右侧显示详情）
            btn = tk.Button(row, text='查看', font=('SimHei', 8),
                           bg='#1E90FF', fg='white', bd=0, width=5,
                           cursor='hand2',
                           command=lambda v=vac: show_detail_in_right_panel(v))
            btn.pack(side=tk.LEFT, padx=1, pady=3)
            
            # 鼠标悬停效果
            def on_enter(e, r=row):
                r.config(bg='#E3F2FD')
            def on_leave(e, r=row, c=bg_color):
                r.config(bg=c)
            
            row.bind('<Enter>', lambda e, r=row: on_enter(e, r))
            row.bind('<Leave>', lambda e, r=row: on_leave(e, r))

        result_label.config(text=f'共 {len(data_list)} 条记录（显示前 {min(len(display_data), 25)} 条）')

    def search_vaccines():
        """执行前端过滤查询 - 显示所有疫苗记录（不限状态）"""
        name = name_var.get().strip()
        category = category_var.get()
        manufacturer = manufacturer_var.get()

        # 显示所有有名称的疫苗记录
        results = [v for v in service.vaccines if v.get('name')]

        # 前端过滤逻辑
        if name:
            results = [v for v in results if name.lower() in str(v.get('name', '')).lower()]

        if category:
            results = [v for v in results if v.get('category') == category]

        if manufacturer:
            results = [v for v in results if v.get('manufacturer') == manufacturer]

        refresh_table(results)

    # 初始加载所有数据
    search_vaccines()


def render_vaccine_edit(parent, service):
    # 疫苗信息修改

    title = tk.Label(parent, text='疫苗信息修改',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)

    # 模式说明
    mode_frame = tk.Frame(parent, bg='#E8F4F8', padx=15, pady=8)
    mode_frame.pack(fill=tk.X, padx=40, pady=(0, 15))

    tk.Label(mode_frame,
            text='💡 支持新增疫苗和编辑已有疫苗。选择要编辑的疫苗后点击"编辑"，或直接填写表单后点击"新增"。',
            font=('SimHei', 10), fg='#1E90FF', bg='#E8F4F8').pack(anchor=tk.W)

    # 选择疫苗区域
    select_frame = tk.LabelFrame(parent, text='选择要编辑的疫苗', font=('SimHei', 11),
                                bg='#F5F5F5', padx=15, pady=10)
    select_frame.pack(fill=tk.X, padx=40, pady=(0, 15))

    select_row = tk.Frame(select_frame, bg='#F5F5F5')
    select_row.pack(fill=tk.X, pady=5)

    tk.Label(select_row, text='选择疫苗：', font=('SimHei', 11), bg='#F5F5F5').pack(side=tk.LEFT)
    
    # 构建疫苗选择列表：格式为 "名称 [批次号]" 以区分不同批次
    vaccine_options = []
    for v in service.vaccines:
        name = v.get('name', '')
        batch = v.get('batch_number', '')
        status = v.get('status', '')
        
        # 显示所有已入库的疫苗（在库、待审核、已驳回都显示）
        if name and (status in ['in_stock', 'pending'] or v.get('stock_time') or v.get('入库时间')):
            if batch:
                display_name = f"{name} [{batch}]"
            else:
                display_name = name
            vaccine_options.append(display_name)
    
    # 去重并排序
    vaccine_options = sorted(list(set(vaccine_options)))
    
    selected_vaccine_var = tk.StringVar()
    vaccine_combo = ttk.Combobox(select_row, textvariable=selected_vaccine_var,
                                values=[''] + vaccine_options, font=('SimHei', 11), width=35,
                                state='readonly')
    vaccine_combo.pack(side=tk.LEFT, padx=(0, 20))

    def load_vaccine_data():
        """加载选中疫苗的数据到表单"""
        nonlocal edit_id
        selected_text = selected_vaccine_var.get()
        if not selected_text:
            messagebox.showwarning('提示', '请先选择要编辑的疫苗')
            return

        # 解析选择项（格式：名称 [批次号] 或 纯名称）
        import re
        match = re.match(r'^(.+?)\s*\[([^\]]+)\]$', selected_text)
        
        if match:
            target_name = match.group(1).strip()
            target_batch = match.group(2).strip()
        else:
            target_name = selected_text.strip()
            target_batch = None
        
        # 查找匹配的疫苗记录（宽松匹配：不限制状态，优先精确匹配）
        found_vaccines = []
        
        for v in (service.vaccines or []):
            v_name = v.get('name', '').strip()
            v_batch = str(v.get('batch_number', '')).strip()
            
            # 名称必须匹配
            if v_name != target_name:
                continue
            
            # 批次号匹配（如果指定了）
            if target_batch and v_batch != target_batch:
                continue
            
            # 收集所有匹配项
            found_vaccines.append(v)
        
        if not found_vaccines:
            # 尝试模糊匹配（忽略批次号，仅按名称查找）
            for v in (service.vaccines or []):
                v_name = v.get('name', '').strip()
                
                # 支持部分匹配（包含关系）
                if target_name in v_name or v_name in target_name:
                    found_vaccines.append(v)
        
        if not found_vaccines:
            messagebox.showerror('错误', 
                f'未找到疫苗记录: {selected_text}\n\n'
                f'请检查：\n'
                f'• 疫苗数据文件是否存在\n'
                f'• 疫苗状态是否为在库/待审核\n'
                f'• 是否需要重新同步数据')
            return
        
        # 使用第一个匹配到的疫苗
        v = found_vaccines[0]
        
        try:
            form_name_var.set(v.get('name', ''))
            category_var.set(v.get('category', ''))
            manufacturer_var.set(v.get('manufacturer', ''))
            batch_var.set(v.get('batch_number', ''))
            prod_date_var.set(v.get('production_date', ''))
            expiry_date_var.set(v.get('expiry_date', ''))
            quantity_var.set(str(v.get('quantity', '')))
            
            # 处理存储类型（兼容新旧字段名）
            vaccine_type = v.get('vaccine_type', v.get('存储温度', v.get('vaccine_type', '冷藏')))
            
            # 转换为标准显示
            if '2-8' in str(vaccine_type) or '冷藏' in str(vaccine_type):
                storage_type_var.set('冷藏')
                temp_display_var.set('2-8')  # 更新温度显示
            elif '-20' in str(vaccine_type) or '冷冻' in str(vaccine_type):
                storage_type_var.set('冷冻')
                temp_display_var.set('-20')  # 更新温度显示
            elif '-70' in str(vaccine_type) or '超低温' in str(vaccine_type):
                storage_type_var.set('超低温')
                temp_display_var.set('-70')  # 更新温度显示
            else:
                storage_type_var.set(str(vaccine_type))
                # 尝试提取数字温度
                import re
                numbers = re.findall(r'-?\d+', str(vaccine_type))
                temp_display_var.set(numbers[0] if numbers else vaccine_type)
                    
            remark_var.set(v.get('remark', ''))
            edit_id = v.get('id')
            
            display_info = f"{target_name}" + (f" [{target_batch}]" if target_batch else '')
            messagebox.showinfo('成功', f'已加载 {display_info} 的数据，可编辑后保存')
            
        except Exception as e:
            messagebox.showerror('加载失败', 
                f'加载数据时发生错误：{str(e)}\n\n'
                f'原始数据：{str(v)[:100]}')

    edit_btn = tk.Button(select_row, text='📝 加载并编辑', command=load_vaccine_data,
                         font=('SimHei', 11), bg='#1E90FF', fg='white', bd=0, width=14)
    edit_btn.pack(side=tk.LEFT)

    # 编辑表单区域
    form_frame = tk.LabelFrame(parent, text='疫苗信息表单', font=('SimHei', 11),
                              bg='#FFFFFF', padx=20, pady=15)
    form_frame.pack(fill=tk.X, padx=40, pady=(0, 15))

    # 表单字段变量
    form_name_var = tk.StringVar()
    category_var = tk.StringVar()
    manufacturer_var = tk.StringVar()
    batch_var = tk.StringVar()
    prod_date_var = tk.StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))
    expiry_date_var = tk.StringVar(value=(datetime.date.today() + datetime.timedelta(days=365)).strftime('%Y-%m-%d'))
    quantity_var = tk.StringVar(value='100')
    storage_type_var = tk.StringVar(value='冷藏')
    remark_var = tk.StringVar()

    # 第一行：疫苗名称 + 类别
    row1 = tk.Frame(form_frame, bg='#FFFFFF')
    row1.pack(fill=tk.X, pady=5)

    tk.Label(row1, text='* 疫苗名称：', font=('SimHei', 11),
            bg='#FFFFFF').pack(side=tk.LEFT)
    tk.Entry(row1, textvariable=form_name_var, font=('SimHei', 11),
            width=18).pack(side=tk.LEFT, padx=(0, 20))
    tk.Label(row1, text='* 类别：', font=('SimHei', 11),
            bg='#FFFFFF').pack(side=tk.LEFT)
    categories = list(set(v.get('category', '') for v in service.vaccines if v.get('category')))
    category_combo = ttk.Combobox(row1, textvariable=category_var,
                                 values=[''] + categories if categories else [''],
                                 font=('SimHei', 11), width=16, state='normal')
    category_combo.pack(side=tk.LEFT)

    # 第二行：生产厂家 + 批次号
    row2 = tk.Frame(form_frame, bg='#FFFFFF')
    row2.pack(fill=tk.X, pady=5)

    tk.Label(row2, text='生产厂家：', font=('SimHei', 11),
            bg='#FFFFFF').pack(side=tk.LEFT)
    manufacturers = list(set(m.get('name', '') for m in service.manufacturers if service.manufacturers))
    mfr_combo = ttk.Combobox(row2, textvariable=manufacturer_var,
                            values=[''] + manufacturers if manufacturers else [''],
                            font=('SimHei', 11), width=16, state='normal')
    mfr_combo.pack(side=tk.LEFT, padx=(0, 20))
    tk.Label(row2, text='批次号：', font=('SimHei', 11),
            bg='#FFFFFF').pack(side=tk.LEFT)
    tk.Entry(row2, textvariable=batch_var, font=('SimHei', 11),
            width=14).pack(side=tk.LEFT)

    # 第三行：生产日期 + 有效期
    row3 = tk.Frame(form_frame, bg='#FFFFFF')
    row3.pack(fill=tk.X, pady=5)

    tk.Label(row3, text='生产日期：', font=('SimHei', 11),
            bg='#FFFFFF').pack(side=tk.LEFT)
    tk.Entry(row3, textvariable=prod_date_var, font=('SimHei', 11),
            width=12).pack(side=tk.LEFT, padx=(0, 20))
    tk.Label(row3, text='* 有效期至：', font=('SimHei', 11),
            bg='#FFFFFF').pack(side=tk.LEFT)
    tk.Entry(row3, textvariable=expiry_date_var, font=('SimHei', 11),
            width=12).pack(side=tk.LEFT)
    tk.Label(row3, text='  (格式: YYYY-MM-DD)', font=('SimHei', 9),
            fg='#999', bg='#FFFFFF').pack(side=tk.LEFT)

    # 第四行：数量 + 存储类型 + 温度显示
    row4 = tk.Frame(form_frame, bg='#FFFFFF')
    row4.pack(fill=tk.X, pady=5)

    tk.Label(row4, text='* 数量(剂)：', font=('SimHei', 11),
            bg='#FFFFFF').pack(side=tk.LEFT)
    tk.Entry(row4, textvariable=quantity_var, font=('SimHei', 11),
            width=10).pack(side=tk.LEFT, padx=(0, 15))
    
    tk.Label(row4, text='存储类型：', font=('SimHei', 11),
            bg='#FFFFFF').pack(side=tk.LEFT)
    
    # 存储类型选择区（左侧）
    type_select_frame = tk.Frame(row4, bg='#FFFFFF')

    tk.Radiobutton(type_select_frame, text='2-8℃冷藏', variable=storage_type_var,
                  value='冷藏', bg='#FFFFFF', font=('SimHei', 10)).pack(side=tk.LEFT, padx=(0, 8))
    tk.Radiobutton(type_select_frame, text='-20℃冷冻', variable=storage_type_var,
                  value='冷冻', bg='#FFFFFF', font=('SimHei', 10)).pack(side=tk.LEFT)
    
    type_select_frame.pack(side=tk.LEFT)
    
    # 温度显示框（右侧 - 只读，显示当前疫苗的实际温度）
    temp_display_var = tk.StringVar(value='未选择疫苗')  # 默认提示
    
    temp_entry = tk.Entry(row4, textvariable=temp_display_var, 
                           font=('SimHei', 11), width=18, 
                           state='readonly', 
                           bg='#F0F0F0',
                           relief=tk.FLAT)
    temp_entry.pack(side=tk.LEFT, padx=(12, 0))
    
    # 摄氏度图标
    celsius_label = tk.Label(row4, text='℃',
                            font=('SimHei', 13, 'bold'), fg='#666', bg='#FFFFFF')
    celsius_label.pack(side=tk.LEFT)

    # 第五行：备注
    row5 = tk.Frame(form_frame, bg='#FFFFFF')
    row5.pack(fill=tk.X, pady=5)
    tk.Label(row5, text='备注：', font=('SimHei', 11),
            bg='#FFFFFF').pack(side=tk.LEFT)
    tk.Entry(row5, textvariable=remark_var, font=('SimHei', 11),
            width=50).pack(side=tk.LEFT, padx=(0, 10))

    # 操作按钮区
    btn_frame = tk.Frame(parent, bg='#FFFFFF')
    btn_frame.pack(pady=20)

    edit_id = None  # 用于存储正在编辑的疫苗ID

    def validate_form():
        """校验表单，收集所有错误后一次性显示"""
        errors = []
        
        if not form_name_var.get().strip():
            errors.append('请填写疫苗名称')
        
        if not category_var.get().strip():
            errors.append('请选择或输入类别')
        elif category_var.get().strip().isdigit():
            errors.append('类别名称不能为纯数字')

        if not manufacturer_var.get().strip():
            errors.append('请选择或输入生产厂家')
        
        if not expiry_date_var.get().strip():
            errors.append('请填写有效期')
        else:
            try:
                datetime.datetime.strptime(expiry_date_var.get(), '%Y-%m-%d')
            except ValueError:
                errors.append('日期格式不正确，请使用 YYYY-MM-DD 格式')
        
        if not quantity_var.get().strip():
            errors.append('请填写数量')
        elif not quantity_var.get().isdigit():
            errors.append('数量必须为数字')
        else:
            qty = int(quantity_var.get())
            if qty <= 0:
                errors.append('数量必须大于0')

        # 批号格式校验
        batch = batch_var.get().strip()
        if batch and not re.match(r'^[A-Za-z0-9\-_]+$', batch):
            errors.append('批号格式不正确，只允许字母、数字、横线、下划线')

        # 日期合理性检查
        prod = prod_date_var.get().strip()
        expiry = expiry_date_var.get().strip()
        if prod and expiry:
            try:
                prod_dt = datetime.datetime.strptime(prod, '%Y-%m-%d').date()
                expiry_dt = datetime.datetime.strptime(expiry, '%Y-%m-%d').date()
                if expiry_dt <= prod_dt:
                    errors.append('有效期必须晚于生产日期')
                if expiry_dt <= datetime.date.today():
                    errors.append('警告：有效期早于或等于今天')
            except ValueError:
                pass  # 格式错误已在前面检查

        if errors:
            messagebox.showerror('表单校验失败', '\n'.join(f'• {e}' for e in errors))
            return False
        
        return True

    def save_new_vaccine():
        """保存新疫苗"""
        if not validate_form():
            return

        try:
            result = service.add_vaccine(
                name=form_name_var.get().strip(),
                category=category_var.get().strip(),
                production_date=prod_date_var.get().strip(),
                expiry_date=expiry_date_var.get().strip(),
                manufacturer=manufacturer_var.get().strip(),
                quantity=int(quantity_var.get()),
                batch_number=batch_var.get().strip() or f'B{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}',
                vaccine_type=storage_type_var.get(),
                remark=remark_var.get().strip()
            )

            action = f"添加疫苗：{result['name']} - {result['quantity']}剂"
            service.log_operation(action)
            messagebox.showinfo('成功', f'疫苗 {result["name"]} 添加成功！\n等待审核入库。')
            clear_form()
        except ValueError as e:
            messagebox.showerror('数据校验失败', str(e))
        except Exception as e:
            messagebox.showerror('添加失败', f'添加疫苗时发生错误：{str(e)}')

    def save_edit_vaccine():
        """保存编辑的疫苗"""
        if not validate_form():
            return
        
        # 使用edit_id（在加载时已设置）来定位要编辑的疫苗
        target_id = edit_id  # 从全局变量获取当前编辑的疫苗ID
        selected_text = selected_vaccine_var.get()
        found = False

        # 方式1：优先使用ID匹配（最准确）
        if target_id:
            for v in (service.vaccines or []):
                # 兼容整数和字符串类型的ID
                if str(v.get('id')) == str(target_id):
                    v['name'] = form_name_var.get().strip()
                    v['category'] = category_var.get().strip()
                    v['production_date'] = prod_date_var.get().strip()
                    v['expiry_date'] = expiry_date_var.get().strip()
                    v['manufacturer'] = manufacturer_var.get().strip()
                    
                    # 安全转换数量为整数
                    try:
                        v['quantity'] = int(quantity_var.get())
                    except ValueError:
                        v['quantity'] = int(float(quantity_var.get())) if quantity_var.get() else 0
                    
                    v['batch_number'] = batch_var.get().strip()
                    v['vaccine_type'] = storage_type_var.get()
                    v['remark'] = remark_var.get().strip()
                    found = True
                    break

        # 方式2：如果ID匹配失败，尝试按名称和批次号匹配
        if not found and selected_text:
            import re
            match = re.match(r'^(.+?)\s*\[([^\]]+)\]$', selected_text)
            
            if match:
                target_name = match.group(1).strip()
                target_batch = match.group(2).strip()
                
                for v in (service.vaccines or []):
                    if v.get('name') == target_name and str(v.get('batch_number', '')) == target_batch:
                        v['name'] = form_name_var.get().strip()
                        v['category'] = category_var.get().strip()
                        v['production_date'] = prod_date_var.get().strip()
                        v['expiry_date'] = expiry_date_var.get().strip()
                        v['manufacturer'] = manufacturer_var.get().strip()
                        
                        try:
                            v['quantity'] = int(quantity_var.get())
                        except ValueError:
                            v['quantity'] = int(float(quantity_var.get())) if quantity_var.get() else 0
                        
                        v['batch_number'] = batch_var.get().strip()
                        v['vaccine_type'] = storage_type_var.get()
                        v['remark'] = remark_var.get().strip()
                        found = True
                        break

        if found:
            service.save_data()
            action = f"修改疫苗：{form_name_var.get()} [{batch_var.get()}]"
            service.log_operation(action)
            messagebox.showinfo('成功', f'✅ 疫苗信息修改成功！\n\n'
                                f'名称：{form_name_var.get()}\n'
                                f'类别：{category_var.get()}\n'
                                f'批次号：{batch_var.get()}')
            clear_form()
        else:
            messagebox.showerror('错误', 
                f'❌ 未找到要编辑的疫苗记录\n\n'
                f'选择项：{selected_text or "(未选择)" }\n'
                f'目标ID：{target_id or "(未加载)" }\n\n'
                f'请重新选择并加载数据后再保存')

    def clear_form():
        """清空表单"""
        form_name_var.set('')
        category_var.set('')
        manufacturer_var.set('')
        batch_var.set('')
        prod_date_var.set(datetime.date.today().strftime('%Y-%m-%d'))
        expiry_date_var.set((datetime.date.today() + datetime.timedelta(days=365)).strftime('%Y-%m-%d'))
        quantity_var.set('100')
        storage_type_var.set('冷藏')
        remark_var.set('')
        selected_vaccine_var.set('')
        
        # 重置编辑ID
        global edit_id
        edit_id = None

    # 按钮
    new_btn = tk.Button(btn_frame, text='➕ 新增疫苗', command=save_new_vaccine,
                       font=('SimHei', 12), bg='#00CC00', fg='white', bd=0, width=14, height=2)
    new_btn.pack(side=tk.LEFT, padx=10)

    save_btn = tk.Button(btn_frame, text='💾 保存修改', command=save_edit_vaccine,
                        font=('SimHei', 12), bg='#FF9900', fg='white', bd=0, width=14, height=2)
    save_btn.pack(side=tk.LEFT, padx=10)

    reset_btn = tk.Button(btn_frame, text='🔄 清空表单', command=clear_form,
                         font=('SimHei', 12), bg='#999999', fg='white', bd=0, width=14, height=2)
    reset_btn.pack(side=tk.LEFT, padx=10)
