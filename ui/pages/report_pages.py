# 统计报表相关页面

import tkinter as tk
from tkinter import ttk


def render_report_center(parent, service):
    # 报表中心

    title = tk.Label(parent, text='📊 报表中心',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)

    # 筛选条件区域
    filter_frame = tk.LabelFrame(parent, text='筛选条件', font=('SimHei', 11),
                                bg='#F5F5F5', padx=15, pady=10)
    filter_frame.pack(fill=tk.X, padx=40, pady=(0, 15))

    row1 = tk.Frame(filter_frame, bg='#F5F5F5')
    row1.pack(fill=tk.X, pady=5)

    tk.Label(row1, text='报表类型：', font=('SimHei', 11),
            bg='#F5F5F5').pack(side=tk.LEFT)
    report_type_var = tk.StringVar(value='入库明细')
    type_combo = ttk.Combobox(row1, textvariable=report_type_var,
                             values=['入库明细', '出库明细', '库存汇总'],
                             state='readonly', width=14, font=('SimHei', 11))
    type_combo.pack(side=tk.LEFT, padx=(0, 20))

    tk.Label(row1, text='时间范围：', font=('SimHei', 11),
            bg='#F5F5F5').pack(side=tk.LEFT)
    time_range_var = tk.StringVar(value='本月')
    time_combo = ttk.Combobox(row1, textvariable=time_range_var,
                             values=['今日', '本周', '本月', '本季度', '本年', '全部'],
                             state='readonly', width=12, font=('SimHei', 11))
    time_combo.pack(side=tk.LEFT, padx=(0, 15))

    query_btn = tk.Button(row1, text='🔍 查询生成', command=lambda: generate_report(),
                         font=('SimHei', 11), bg='#1E90FF', fg='white', bd=0, width=12)
    query_btn.pack(side=tk.LEFT)

    # 说明文字
    note_frame = tk.Frame(parent, bg='#E8F4F8', padx=15, pady=8)
    note_frame.pack(fill=tk.X, padx=40, pady=(0, 10))
    tk.Label(note_frame,
            text='💡 前端聚合数据生成报表。Excel/CSV导出功能开发中。',
            font=('SimHei', 10), fg='#1E90FF', bg='#E8F4F8').pack(anchor=tk.W)

    # 结果统计标签
    result_label = tk.Label(parent, text='', font=('SimHei', 10), fg='#666', bg='#FFFFFF')
    result_label.pack(anchor=tk.W, padx=40)

    # 表格容器 - 使用 Treeview 替代手动 Label 表格，支持水平+垂直滚动
    table_container = tk.Frame(parent, bg='#FFFFFF')
    table_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 15))

    # Treeview 框架
    tree_frame = tk.Frame(table_container)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    # 垂直滚动条和水平滚动条
    vsb = ttk.Scrollbar(tree_frame, orient="vertical")
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal")

    # 创建 Treeview（初始列在 generate_report 中动态配置）
    tree = ttk.Treeview(tree_frame, yscrollcommand=vsb.set, xscrollcommand=hsb.set,
                        show='headings', height=15, style='Report.Treeview')

    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)

    # 布局
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 设置 Treeview 样式（同时保留斑马纹 tag）
    style = ttk.Style()
    style.configure('Report.Treeview', font=('SimHei', 10), rowheight=28)
    style.configure('Report.Treeview.Heading', font=('SimHei', 11, 'bold'), background='#2C3E50', foreground='white')
    style.map('Report.Treeview', background=[('selected', '#3498DB')])
    style.map('Report.Treeview.Heading', background=[('active', '#34495E')])

    tree.tag_configure('even', background='#FFFFFF')
    tree.tag_configure('odd', background='#F5F5F5')

    def get_date_range():
        """根据时间范围返回起止日期"""
        import datetime as dt

        range_name = time_range_var.get()
        today = dt.date.today()

        if range_name == '今日':
            return str(today), str(today)
        elif range_name == '本周':
            start = today - dt.timedelta(days=today.weekday())
            return str(start), str(today)
        elif range_name == '本月':
            start = today.replace(day=1)
            return str(start), str(today)
        elif range_name == '本季度':
            quarter = (today.month - 1) // 3 + 1
            start = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            return str(start), str(today)
        elif range_name == '本年':
            start = today.replace(month=1, day=1)
            return str(start), str(today)
        else:  # 全部
            return '2020-01-01', str(today)

    def _configure_tree_columns(columns, column_widths):
        """配置 Treeview 列"""
        tree['columns'] = columns
        for col, width in zip(columns, column_widths):
            tree.heading(col, text=col, anchor='center')
            tree.column(col, width=width, minwidth=60, anchor='center')

    def _clear_and_fill_tree(data_rows):
        """清空并填充 Treeview 数据"""
        for item in tree.get_children():
            tree.delete(item)
        for idx, row_values in enumerate(data_rows):
            tag = 'even' if idx % 2 == 0 else 'odd'
            tree.insert('', tk.END, values=row_values, tags=(tag,))

    def generate_report():
        """根据类型和时间范围生成报表"""
        report_type = report_type_var.get()
        start_date, end_date = get_date_range()

        # 根据报表类型配置不同的列和数据
        if report_type == '入库明细':
            columns = ['单号', '名称', '批号', '数量', '日期']
            column_widths = [160, 160, 120, 80, 140]
            _configure_tree_columns(columns, column_widths)

            results = []
            for v in service.vaccines:
                in_time = v.get('入库时间', '')
                if not in_time:
                    continue
                try:
                    date_part = in_time.split(' ')[0]
                    if start_date <= date_part <= end_date:
                        results.append(v)
                except (IndexError, ValueError):
                    continue

            results.sort(key=lambda x: x.get('入库时间', ''), reverse=True)
            display_data = results[:30]

            rows = []
            for item in display_data:
                rows.append((
                    item.get('入库单号', '-'),
                    item.get('name', '-'),
                    item.get('batch_number', '-'),
                    item.get('quantity', 0),
                    item.get('入库时间', '-')
                ))
            _clear_and_fill_tree(rows)
            result_label.config(text=f'📊 {report_type} | 时间: {start_date} ~ {end_date} | 共 {len(results)} 条记录（显示前{len(display_data)}条）')

        elif report_type == '出库明细':
            columns = ['出库单号', '名称', '领用人', '数量', '用途', '时间']
            column_widths = [170, 140, 110, 70, 130, 160]
            _configure_tree_columns(columns, column_widths)

            results = []
            outbound_records = service.get_outbound_records({
                'start_date': start_date,
                'end_date': end_date
            }) if hasattr(service, 'get_outbound_records') else []

            for record in outbound_records:
                out_time = record.get('outbound_time', '')
                results.append({
                    '出库单号': record.get('outbound_id', '-'),
                    'vaccine_name': record.get('vaccine_name', '-'),
                    '领用人': record.get('recipient_unit_name', '-'),
                    '数量': record.get('quantity', 0),
                    '用途': record.get('outbound_type', '-'),
                    '出库时间': out_time
                })

            results.sort(key=lambda x: x.get('出库时间', ''), reverse=True)
            display_data = results[:30]

            rows = []
            for item in display_data:
                rows.append((
                    item.get('出库单号', '-'),
                    item.get('vaccine_name', '-'),
                    item.get('领用人', '-'),
                    item.get('数量', 0),
                    item.get('用途', '-'),
                    item.get('出库时间', '-')
                ))
            _clear_and_fill_tree(rows)
            result_label.config(text=f'📊 {report_type} | 时间: {start_date} ~ {end_date} | 共 {len(results)} 条记录（显示前{len(display_data)}条）')

        else:  # 库存汇总
            columns = ['名称', '类别', '厂家', '当前库存', '状态']
            column_widths = [140, 130, 160, 90, 80]
            _configure_tree_columns(columns, column_widths)

            import datetime as dt

            results = []
            for v in service.vaccines:
                if v.get('status') != 'in_stock':
                    continue

                status_text = '正常'
                try:
                    expiry = dt.datetime.strptime(v.get('expiry_date', ''), '%Y-%m-%d').date()
                    days_left = (expiry - dt.date.today()).days
                    if days_left < 0:
                        status_text = '已过期'
                    elif days_left <= 30:
                        status_text = '预警'
                except (ValueError, TypeError):
                    pass

                results.append((v, status_text))

            display_data = results[:30]

            rows = []
            for v_item, status_t in display_data:
                rows.append((
                    v_item.get('name', '-'),
                    v_item.get('category', '-'),
                    v_item.get('manufacturer', '-'),
                    v_item.get('quantity', 0),
                    status_t
                ))
            _clear_and_fill_tree(rows)
            result_label.config(text=f'📊 {report_type} | 共 {len(results)} 条在库记录（显示前{len(display_data)}条）')

    # 初始加载默认报表
    generate_report()

    # 绑定报表类型和时间范围的变化事件，自动刷新
    type_combo.bind('<<ComboboxSelected>>', lambda e: generate_report())
    time_combo.bind('<<ComboboxSelected>>', lambda e: generate_report())


# ==================== 库存统计 ====================

def render_inventory_stat(parent, service):
    # 库存统计页面

    # 创建 Notebook 容器
    notebook = ttk.Notebook(parent)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ===== Tab1: 库存概览 =====
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text='  📊 库存概览  ')
    _build_tab1_dashboard(tab1, service)

    # ===== Tab2: 效期分析 =====
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text='  ⏰ 效期分析  ')
    _build_tab2_expiry_analysis(tab2, service)

    # ===== Tab3: 进销存报表 =====
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text='  📈 进销存报表  ')
    _build_tab3_flow_report(tab3, service)


# ==================== 辅助函数 ====================

def _create_kpi_card(parent, title, value, bg_color, subtitle=''):
    """创建 KPI 数字卡片"""
    card = tk.Frame(parent, bg=bg_color, padx=25, pady=18)
    card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 8))

    tk.Label(card, text=title, font=('SimHei', 11),
            fg='white', bg=bg_color).pack(anchor='w')
    
    value_label = tk.Label(card, text=value, font=('SimHei', 32, 'bold'),
                          fg='white', bg=bg_color)
    value_label.pack(pady=(8, 0))
    
    if subtitle:
        tk.Label(card, text=subtitle, font=('SimHei', 9),
                fg='#EEEEEE', bg=bg_color).pack(anchor='w', pady=(4, 0))


def _create_status_kpi_card(parent, title, varieties, quantity, 
                            bg_color, action_text=''):
    """创建时效状态 KPI 卡片"""
    card = tk.Frame(parent, bg=bg_color, padx=20, pady=15)
    card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 8))

    tk.Label(card, text=title, font=('SimHei', 13, 'bold'),
            fg='white', bg=bg_color).pack(anchor='w')
    
    info_frame = tk.Frame(card, bg=bg_color)
    info_frame.pack(fill=tk.X, pady=(8, 0))
    
    tk.Label(info_frame, text=f'品种数: {varieties}', font=('SimHei', 12),
            fg='white', bg=bg_color).pack(side=tk.LEFT, padx=(0, 15))
    tk.Label(info_frame, text=f'总剂数: {quantity}', font=('SimHei', 12),
            fg='white', bg=bg_color).pack(side=tk.LEFT)
    
    if action_text:
        action_label = tk.Label(card, text=action_text, font=('SimHei', 10, 'underline'),
                               fg='#FFFF00', bg=bg_color, cursor='hand2')
        action_label.pack(anchor='w', pady=(6, 0))


def _create_treeview_table(parent, columns, column_headers,
                          show_headings=True, height=8):
    # 创建 Treeview 表格
    
    tree = ttk.Treeview(parent, columns=columns, show='headings' if show_headings else '',
                       height=height)
    
    # 设置表头样式
    style = ttk.Style()
    style.configure('Treeview.Heading', font=('SimHei', 11, 'bold'), background='#2C3E50',
                   foreground='white')
    style.configure('Treeview', font=('SimHei', 10), rowheight=28)
    style.map('Treeview', background=[('selected', '#3498DB')])
    
    for col in columns:
        tree.heading(col, text=column_headers.get(col, col), anchor='center')
        tree.column(col, width=100, minwidth=60, anchor='center')
    
    return tree


def _setup_table_scrollbar(tree, parent):
    # 添加滚动条
    vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    return vsb, hsb


def _insert_treeview_data(tree, data_rows):
    """向表格插入数据并应用斑马纹"""
    for idx, row_data in enumerate(data_rows):
        tag = 'even' if idx % 2 == 0 else 'odd'
        
        if isinstance(row_data, dict):
            values = tuple(row_data.values())
        else:
            values = tuple(row_data)
        
        tree.insert('', tk.END, values=values, tags=(tag,))
    
    # 设置斑马纹颜色（使用 Treeview 的 tag_configure 方法）
    tree.tag_configure('even', background='#FFFFFF')
    tree.tag_configure('odd', background='#F5F5F5')


# ==================== Tab1: 库存概览实现 ====================

def _build_tab1_dashboard(parent, service):
    """构建 Tab1: 库存概览页面 - 重新设计版"""

    # 使用 Canvas 实现整体滚动
    main_canvas = tk.Canvas(parent, bg='#FFFFFF', highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=main_canvas.yview)
    scrollable_frame = tk.Frame(main_canvas, bg='#FFFFFF')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )
    
    main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=scrollbar.set)

    # 动态更新 canvas 内部窗口的宽度以匹配父容器
    def on_canvas_configure(event):
        main_canvas.itemconfig(main_canvas.find_all()[0], width=event.width)
    main_canvas.bind('<Configure>', on_canvas_configure)

    def on_mousewheel(event):
        main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    main_canvas.bind_all("<MouseWheel>", on_mousewheel)

    # ===== 顶部：4格 KPI 卡片区 =====
    kpi_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
    kpi_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

    stats = service.get_dashboard_stats()
    kpi = stats['kpi']

    # 4格KPI卡片配置
    card_configs = [
        ('📦 库存总剂数', f'{kpi["total_quantity"]:,}', '#27AE60'),
        ('⚠️ 预警品种数', f'{kpi["warning_varieties"]}', '#FF9900'),
        ('❌ 过期品种数', f'{kpi["expired_varieties"]}', '#DC3545'),
        ('🏭 冷库利用率', f'{kpi["avg_storage_usage"]}%', '#17A2B8'),
    ]

    cards_row = tk.Frame(kpi_frame, bg='#FFFFFF')
    cards_row.pack(fill=tk.X)
    
    for i, (title, value, color) in enumerate(card_configs):
        card = tk.Frame(cards_row, bg=color, padx=15, pady=12)
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0 if i == 0 else 6, 6 if i < 3 else 0))
        
        tk.Label(card, text=title, font=('SimHei', 10),
                fg='white', bg=color).pack(anchor='w')
        tk.Label(card, text=value, font=('SimHei', 28, 'bold'),
                fg='white', bg=color).pack(pady=(5, 0))

    # ===== 中部：维度分布表格区（左右两栏）=====
    distribution_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
    distribution_frame.pack(fill=tk.X, padx=15, pady=(10, 10))

    # 左栏：按类别 + 按厂家
    left_col = tk.Frame(distribution_frame, bg='#FFFFFF')
    left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

    # 按类别分布
    cat_lf = tk.LabelFrame(left_col, text=' 按类别分布 ', font=('SimHei', 10, 'bold'), bg='#FFFFFF')
    cat_lf.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

    cat_tree = ttk.Treeview(cat_lf, columns=('cat', 'qty', 'pct', 'cnt'), show='headings', height=4,
                            style='Dashboard.Treeview')
    cat_tree.heading('cat', text='类别'); cat_tree.column('cat', width=100, anchor='center')
    cat_tree.heading('qty', text='数量'); cat_tree.column('qty', width=80, anchor='center')
    cat_tree.heading('pct', text='占比%'); cat_tree.column('pct', width=70, anchor='center')
    cat_tree.heading('cnt', text='品种数'); cat_tree.column('cnt', width=60, anchor='center')

    for d in stats['category_distribution']:
        cat_tree.insert('', 'end', values=(d['category'], d['quantity'], f"{d['percentage']}%", d['variety_count']))

    cat_vsb = ttk.Scrollbar(cat_lf, orient="vertical", command=cat_tree.yview)
    cat_tree.configure(yscrollcommand=cat_vsb.set)
    cat_vsb.pack(side=tk.RIGHT, fill=tk.Y)
    cat_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 按厂家分布
    mf_lf = tk.LabelFrame(left_col, text=' 按厂家分布 ', font=('SimHei', 10, 'bold'), bg='#FFFFFF')
    mf_lf.pack(fill=tk.BOTH, expand=True)

    mf_tree = ttk.Treeview(mf_lf, columns=('mf', 'qty', 'pct', 'cnt'), show='headings', height=4,
                           style='Dashboard.Treeview')
    mf_tree.heading('mf', text='厂家名称'); mf_tree.column('mf', width=120, anchor='center')
    mf_tree.heading('qty', text='数量'); mf_tree.column('qty', width=70, anchor='center')
    mf_tree.heading('pct', text='占比%'); mf_tree.column('pct', width=65, anchor='center')
    mf_tree.heading('cnt', text='品种数'); mf_tree.column('cnt', width=55, anchor='center')

    for d in stats['manufacturer_distribution']:
        mf_tree.insert('', 'end', values=(d['manufacturer'][:14], d['quantity'], f"{d['percentage']}%", d['variety_count']))

    mf_vsb = ttk.Scrollbar(mf_lf, orient="vertical", command=mf_tree.yview)
    mf_tree.configure(yscrollcommand=mf_vsb.set)
    mf_vsb.pack(side=tk.RIGHT, fill=tk.Y)
    mf_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 右栏：按冷库分布
    right_col = tk.Frame(distribution_frame, bg='#FFFFFF')
    right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

    stg_lf = tk.LabelFrame(right_col, text=' 按冷库分布 ', font=('SimHei', 10, 'bold'), bg='#FFFFFF')
    stg_lf.pack(fill=tk.BOTH, expand=True)

    stg_tree = ttk.Treeview(stg_lf, columns=('id', 'name', 'type', 'cap', 'used', 'rate', 'cnt'), 
                           show='headings', height=min(len(stats['storage_distribution'])+1, 7),
                           style='Dashboard.Treeview')
    stg_tree.heading('id', text='ID'); stg_tree.column('id', width=40, anchor='center')
    stg_tree.heading('name', text='冷库名称'); stg_tree.column('name', width=110, anchor='center')
    stg_tree.heading('type', text='类型'); stg_tree.column('type', width=85, anchor='center')
    stg_tree.heading('cap', text='容量'); stg_tree.column('cap', width=55, anchor='center')
    stg_tree.heading('used', text='已用'); stg_tree.column('used', width=50, anchor='center')
    stg_tree.heading('rate', text='使用率'); stg_tree.column('rate', width=60, anchor='center')
    stg_tree.heading('cnt', text='品种'); stg_tree.column('cnt', width=45, anchor='center')

    for d in stats['storage_distribution']:
        stg_tree.insert('', 'end', values=(d['storage_id'], d['name'][:12], d['type'],
                                          d['capacity'], d['used'], f"{d['usage_rate']}%", d['variety_count']))

    stg_vsb = ttk.Scrollbar(stg_lf, orient="vertical", command=stg_tree.yview)
    stg_tree.configure(yscrollcommand=stg_vsb.set)
    stg_vsb.pack(side=tk.RIGHT, fill=tk.Y)
    stg_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ===== 下部：ABC 分类分析区 =====
    abc_lf = tk.LabelFrame(scrollable_frame, text=' ABC 分类分析（按库存量占比） ',
                          font=('SimHei', 10, 'bold'), bg='#FFFFFF')
    abc_lf.pack(fill=tk.X, padx=15, pady=(10, 20))

    # ABC汇总表格
    sum_lf = tk.LabelFrame(abc_lf, text=' 分类汇总 ', font=('SimHei', 9), bg='#FFFFFF')
    sum_lf.pack(fill=tk.X, padx=8, pady=(8, 5))

    abc_summary = service.get_abc_classification()['summary']
    
    sum_tree = ttk.Treeview(sum_lf, columns=('cls', 'cnt', 'qty', 'ratio', 'strategy'), 
                           show='headings', height=3, style='Dashboard.Treeview')
    sum_tree.heading('cls', text='分类'); sum_tree.column('cls', width=120, anchor='center')
    sum_tree.heading('cnt', text='品种数'); sum_tree.column('cnt', width=60, anchor='center')
    sum_tree.heading('qty', text='库存量'); sum_tree.column('qty', width=70, anchor='center')
    sum_tree.heading('ratio', text='占比%'); sum_tree.column('ratio', width=60, anchor='center')
    sum_tree.heading('strategy', text='管理策略'); sum_tree.column('strategy', width=220, anchor='w')

    class_data = [
        ('🔴 A类(重点管理)', abc_summary['class_A']['count'], abc_summary['class_A']['quantity'],
         f"{abc_summary['class_A']['ratio']}%", '每日盘点、优先出库、严格监控'),
        ('🟡 B类(一般管理)', abc_summary['class_B']['count'], abc_summary['class_B']['quantity'],
         f"{abc_summary['class_B']['ratio']}%", '周度检查、常规管理、定期复核'),
        ('🟢 C类(宽松管理)', abc_summary['class_C']['count'], abc_summary['class_C']['quantity'],
         f"{abc_summary['class_C']['ratio']}%", '月度抽查、简化流程、降低成本'),
    ]
    for row in class_data:
        sum_tree.insert('', 'end', values=row)
    sum_tree.pack(fill=tk.X, padx=5, pady=5)

    # ABC明细表格
    det_lf = tk.LabelFrame(abc_lf, text=' 各品种分类详情 ', font=('SimHei', 9), bg='#FFFFFF')
    det_lf.pack(fill=tk.X, padx=8, pady=(5, 8))

    abc_details = service.get_abc_classification()['details']
    det_tree = ttk.Treeview(det_lf, columns=('cls', 'name', 'qty', 'pct', 'cum'), 
                          show='headings', height=5, style='Dashboard.Treeview')
    det_tree.heading('cls', text='分类'); det_tree.column('cls', width=60, anchor='center')
    det_tree.heading('name', text='品种名称'); det_tree.column('name', width=130, anchor='center')
    det_tree.heading('qty', text='库存量'); det_tree.column('qty', width=80, anchor='center')
    det_tree.heading('pct', text='占比%'); det_tree.column('pct', width=70, anchor='center')
    det_tree.heading('cum', text='累计占比%'); det_tree.column('cum', width=80, anchor='center')

    icons = {'A': '🔴A', 'B': '🟡B', 'C': '🟢C'}
    for d in abc_details:
        det_tree.insert('', 'end', values=(icons[d['abc_class']], d['name'], d['quantity'],
                                           f"{d['percentage']}%", f"{d['cumulative']}%"))

    det_vsb = ttk.Scrollbar(det_lf, orient="vertical", command=det_tree.yview)
    det_tree.configure(yscrollcommand=det_vsb.set)
    det_vsb.pack(side=tk.RIGHT, fill=tk.Y)
    det_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 滚动条布局
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


# ==================== Tab2: 效期分析实现 ====================

def _build_tab2_expiry_analysis(parent, service):
    """构建 Tab2: 效期分析页面 - 重新设计版"""

    # 使用 Canvas 实现整体滚动
    main_canvas = tk.Canvas(parent, bg='#FFFFFF', highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=main_canvas.yview)
    scrollable_frame = tk.Frame(main_canvas, bg='#FFFFFF')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )
    
    main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=scrollbar.set)

    def on_canvas_configure(event):
        main_canvas.itemconfig(main_canvas.find_all()[0], width=event.width)
    main_canvas.bind('<Configure>', on_canvas_configure)

    def on_mousewheel(event):
        main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    main_canvas.bind_all("<MouseWheel>", on_mousewheel)

    # 获取效期统计数据
    expiry_stats = service.get_expiry_tier_stats()
    tiers = expiry_stats['tiers']

    # ===== 顶部：3层时效状态卡片区 =====
    tier_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
    tier_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

    tier_configs = [
        ('🔴 已过期', tiers['expired']['varieties'], tiers['expired']['quantity'], '#DC3545', '[立即处理]'),
        ('🠮 ≤30天临期', tiers['warning']['varieties'], tiers['warning']['quantity'], '#FF9900', '[优先出库]'),
        ('✅ 安全>30天', tiers['safe']['varieties'], tiers['safe']['quantity'], '#28A745', ''),
    ]

    for title, varieties, qty, color, action in tier_configs:
        card = tk.Frame(tier_frame, bg=color, padx=18, pady=12)
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 6))
        
        tk.Label(card, text=title, font=('SimHei', 11, 'bold'),
                fg='white', bg=color).pack(anchor='w')
        
        info = tk.Frame(card, bg=color)
        info.pack(fill=tk.X, pady=(6, 0))
        
        tk.Label(info, text=f'品种: {varieties}  |  总剂: {qty}', font=('SimHei', 10),
                fg='white', bg=color).pack(anchor='w')
        
        if action:
            tk.Label(card, text=action, font=('SimHei', 9), fg='#FFFF00',
                    bg=color, cursor='hand2').pack(anchor='w', pady=(4, 0))

    # ===== 中部：临期疫苗明细表 =====
    exp_lf = tk.LabelFrame(scrollable_frame, text=' 临期疫苗明细（按剩余天数升序） ',
                          font=('SimHei', 10, 'bold'), bg='#FFFFFF')
    exp_lf.pack(fill=tk.X, padx=15, pady=(10, 10))

    exp_tree = ttk.Treeview(exp_lf, columns=('name', 'batch', 'days', 'qty', 'storage', 'tier'),
                           show='headings', height=5, style='Dashboard.Treeview')
    exp_tree.heading('name', text='品种名称'); exp_tree.column('name', width=110, anchor='center')
    exp_tree.heading('batch', text='批次号'); exp_tree.column('batch', width=100, anchor='center')
    exp_tree.heading('days', text='剩余天'); exp_tree.column('days', width=65, anchor='center')
    exp_tree.heading('qty', text='库存'); exp_tree.column('qty', width=60, anchor='center')
    exp_tree.heading('storage', text='冷库'); exp_tree.column('storage', width=95, anchor='center')
    exp_tree.heading('tier', text='状态'); exp_tree.column('tier', width=90, anchor='center')

    urgent_items = [d for d in expiry_stats['details'] if d['tier'] in ['expired', 'warning']]
    urgent_items.sort(key=lambda x: x['days_remaining'])

    tier_display = {'expired': '🔴 已过期', 'warning': '🠮 临期预警'}
    if urgent_items:
        for d in urgent_items[:25]:
            exp_tree.insert('', 'end', values=(d['name'][:13], d['batch_number'], d['days_remaining'],
                                            d['quantity'], d['storage_name'][:10], tier_display[d['tier']]))
    else:
        exp_tree.insert('', 'end', values=('暂无过期或临期疫苗', '', '', '', '', ''))

    exp_vsb = ttk.Scrollbar(exp_lf, orient="vertical", command=exp_tree.yview)
    exp_tree.configure(yscrollcommand=exp_vsb.set)
    exp_vsb.pack(side=tk.RIGHT, fill='y')
    exp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # ===== 下部：左右分栏 近效期优先出库率 + 完整明细 =====
    bottom_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
    bottom_frame.pack(fill=tk.X, padx=15, pady=(10, 20))

    # === 左侧：近效期优先出库执行率面板 ===
    fefo_lf = tk.LabelFrame(bottom_frame, text=' 近效期优先出库执行率 ',
                            font=('SimHei', 10, 'bold'), bg='#FFFFFF')
    fefo_lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

    fefo_inner = tk.Frame(fefo_lf, bg='#FFFFFF')
    fefo_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    fefo_result = service.get_fefo_compliance_rate()

    if fefo_result['is_simulation']:
        # 无数据时显示说明
        tk.Label(fefo_inner, text='N/A', font=('SimHei', 42, 'bold'),
                fg='#999999', bg='#FFFFFF').pack()
        tk.Label(fefo_inner, text='暂无出库数据', font=('SimHei', 11),
                fg='#666666', bg='#FFFFFF').pack(pady=(3, 8))
        
        desc_box = tk.Frame(fefo_inner, bg='#FFF9E6', padx=10, pady=8)
        desc_box.pack(fill=tk.X)
        tk.Label(desc_box, text='判定规则：', font=('SimHei', 9, 'bold'),
                fg='#333', bg='#FFF9E6').pack(anchor='w')
        tk.Label(desc_box, text=fefo_result['formula_description'].split('\n\n')[0],
                font=('SimHei', 8), fg='#666', bg='#FFF9E6', justify=tk.LEFT).pack(anchor='w', pady=(3, 0))

        example = fefo_result.get('example')
        if example:
            ex_box = tk.Frame(fefo_inner, bg='#E8F4F8', padx=10, pady=8)
            ex_box.pack(fill=tk.X, pady=(8, 0))
            
            tk.Label(ex_box, text=f"📋 {example.get('scenario', '')}",
                    font=('SimHei', 9, 'bold'), fg='#1E90FF', bg='#E8F4F8').pack(anchor='w')
            for batch in example.get('batches', []):
                tk.Label(ex_box,
                        text=f"   • {batch['batch']}: 效期 {batch['expiry']}, 库存 {batch['quantity']}剂",
                        font=('SimHei', 8), fg='#333', bg='#E8F4F8').pack(anchor='w')
            tk.Label(ex_box, text=f"\n   ✅ {example.get('correct_outbound', '')}",
                    font=('SimHei', 8, 'bold'), fg='#28A745', bg='#E8F4F8').pack(anchor='w', pady=(4, 1))
            tk.Label(ex_box, text=f"   ❌ {example.get('if_outbound_B002', '')}",
                    font=('SimHei', 8), fg='#DC3545', bg='#E8F4F8').pack(anchor='w')
    else:
        rate = fefo_result['compliance_rate']
        rate_color = '#28A745' if rate >= 80 else '#FF9900' if rate >= 60 else '#DC3545'
        
        tk.Label(fefo_inner, text=f'{rate}%', font=('SimHei', 42, 'bold'),
                fg=rate_color, bg='#FFFFFF').pack()
        tk.Label(fefo_inner, text=f"符合近效期优先: {fefo_result['compliant_count']}/{fefo_result['total_records']} 条",
                font=('SimHei', 10), fg='#333', bg='#FFFFFF').pack(pady=(4, 8))
        
        rule_box = tk.Frame(fefo_inner, bg='#F5F5F5', padx=10, pady=6)
        rule_box.pack(fill=tk.X)
        tk.Label(rule_box, text='判定规则：出库时优先选择效期最近的批次',
                font=('SimHei', 8), fg='#666', bg='#F5F5F5', justify=tk.LEFT).pack(anchor='w')

    # === 右侧：效期完整明细表 ===
    dtl_lf = tk.LabelFrame(bottom_frame, text=' 效期完整明细（全部在库） ',
                            font=('SimHei', 10, 'bold'), bg='#FFFFFF')
    dtl_lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    dtl_tree = ttk.Treeview(dtl_lf, columns=('name', 'batch', 'expiry', 'days', 'ratio', 'qty', 'tier'),
                           show='headings', height=10, style='Dashboard.Treeview')
    dtl_tree.heading('name', text='名称'); dtl_tree.column('name', width=90, anchor='center')
    dtl_tree.heading('batch', text='批次'); dtl_tree.column('batch', width=75, anchor='center')
    dtl_tree.heading('expiry', text='效期'); dtl_tree.column('expiry', width=85, anchor='center')
    dtl_tree.heading('days', text='剩余天'); dtl_tree.column('days', width=55, anchor='center')
    dtl_tree.heading('ratio', text='剩余%'); dtl_tree.column('ratio', width=58, anchor='center')
    dtl_tree.heading('qty', text='库存'); dtl_tree.column('qty', width=52, anchor='center')
    dtl_tree.heading('tier', text='状态'); dtl_tree.column('tier', width=68, anchor='center')

    all_details = sorted(expiry_stats['details'], key=lambda x: x['days_remaining'])
    ts_map = {'expired': '🔴过期', 'warning': '🠮临期', 'safe': '✅安全'}
    for d in all_details[:35]:
        dtl_tree.insert('', 'end', values=(
            d['name'][:10], d['batch_number'][:10], d['expiry_date'], d['days_remaining'],
            f"{d['remaining_ratio']:.1f}%", d['quantity'], ts_map[d['tier']]
        ))

    dtl_vsb = ttk.Scrollbar(dtl_lf, orient="vertical", command=dtl_tree.yview)
    dtl_tree.configure(yscrollcommand=dtl_vsb.set)
    dtl_vsb.pack(side=tk.RIGHT, fill='y')
    dtl_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # 设置统一样式
    style = ttk.Style()
    style.configure('Dashboard.Treeview', font=('SimHei', 9), rowheight=26)
    style.configure('Dashboard.Treeview.Heading', font=('SimHei', 9, 'bold'))
    style.map('Dashboard.Treeview', background=[('selected', '#3498DB')])

    # 滚动条布局
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


# ==================== Tab3: 进销存报表实现 ====================

def _build_tab3_flow_report(parent, service):
    """构建 Tab3: 进销存报表页面"""

    # 顶部：时间筛选栏
    filter_frame = tk.Frame(parent, bg='#F5F5F5', padx=15, pady=10)
    filter_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(filter_frame, text='时间范围：', font=('SimHei', 11),
            bg='#F5F5F5').pack(side=tk.LEFT)

    time_var = tk.StringVar(value='本月')
    time_options = ['今日', '本周', '本月', '本季', '本年', '全部']
    time_combo = ttk.Combobox(filter_frame, textvariable=time_var,
                             values=time_options, state='readonly', width=10, font=('SimHei', 10))
    time_combo.pack(side=tk.LEFT, padx=(5, 15))

    query_btn = tk.Button(filter_frame, text='🔍 查询', 
                         command=lambda: refresh_all_tables(),
                         font=('SimHei', 10), bg='#1E90FF', fg='white', bd=0)
    query_btn.pack(side=tk.LEFT)

    # 结果容器（使用Canvas滚动）
    content_canvas = tk.Canvas(parent, bg='#FFFFFF', highlightthickness=0)
    content_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=content_canvas.yview)
    content_frame = tk.Frame(content_canvas, bg='#FFFFFF')
    
    content_frame.bind(
        "<Configure>",
        lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all"))
    )
    
    content_canvas.create_window((0, 0), window=content_frame, anchor="nw")
    content_canvas.configure(yscrollcommand=content_scrollbar.set)

    def get_date_range():
        """获取选定的时间范围"""
        import datetime as dt
        range_name = time_var.get()
        today = dt.date.today()
        
        if range_name == '今日':
            return str(today), str(today)
        elif range_name == '本周':
            start = today - dt.timedelta(days=today.weekday())
            return str(start), str(today)
        elif range_name == '本月':
            start = today.replace(day=1)
            return str(start), str(today)
        elif range_name == '本季':
            quarter = (today.month - 1) // 3 + 1
            start = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            return str(start), str(today)
        elif range_name == '本年':
            start = today.replace(month=1, day=1)
            return str(start), str(today)
        else:
            return None, dt.datetime.now().strftime('%Y-%m-%d')

    def refresh_all_tables():
        """刷新所有表格数据"""
        start_date, end_date = get_date_range()
        _refresh_flow_table(start_date, end_date)
        _refresh_type_table(start_date, end_date)
        _refresh_forecast_panel()
        _refresh_timeline_table(start_date, end_date)

    # ===== 上部：进销存汇总表 =====
    flow_lf = tk.LabelFrame(content_frame, text=' 进销存汇总 ',
                            font=('SimHei', 11, 'bold'), bg='#FFFFFF')
    flow_lf.pack(fill=tk.X, padx=15, pady=(10, 5))

    flow_columns = ('name', 'category', 'opening_stock', 'inbound_quantity', 
                   'outbound_quantity', 'closing_stock', 'change_rate')
    flow_headers = {
        'name': '疫苗名称',
        'category': '类别',
        'opening_stock': '期初库存',
        'inbound_quantity': '本期入库',
        'outbound_quantity': '本期出库',
        'closing_stock': '期末结存',
        'change_rate': '变动率%'
    }
    flow_tree = _create_treeview_table(flow_lf, flow_columns, flow_headers, height=5)
    
    fl_vsb, fl_hsb = _setup_table_scrollbar(flow_tree, flow_lf)
    fl_vsb.pack(side=tk.RIGHT, fill=tk.Y)
    fl_hsb.pack(side=tk.BOTTOM, fill=tk.X)
    flow_tree.pack(fill=tk.BOTH, expand=True)

    def _refresh_flow_table(start_date, end_date):
        """刷新进销存汇总表"""
        for item in flow_tree.get_children():
            flow_tree.delete(item)
        
        data = service.get_inventory_flow_summary(start_date, end_date)['summary']
        
        for row in data:
            change = row['change_rate']
            if change > 0:
                trend_str = f'+{change}% ↑'
                trend_tag = 'trend_up'
            elif change < 0:
                trend_str = f'{change}% ↓'
                trend_tag = 'trend_down'
            else:
                trend_str = '0% →'
                trend_tag = 'trend_stable'
            
            flow_tree.insert('', tk.END, values=(
                row['name'], row['category'], row['opening_stock'],
                row['inbound_quantity'], row['outbound_quantity'],
                row['closing_stock'], trend_str
            ), tags=(trend_tag,))
        
        # 趋势颜色标签（使用 Treeview 的 tag_configure 方法）
        flow_tree.tag_configure('trend_up', foreground='#28A745')
        flow_tree.tag_configure('trend_down', foreground='#DC3545')
        flow_tree.tag_configure('trend_stable', foreground='#999999')

    # ===== 中部左右分栏：业务类型统计 + 趋势预测 =====
    middle_frame = tk.Frame(content_frame, bg='#FFFFFF')
    middle_frame.pack(fill=tk.X, padx=15, pady=10)

    # 中部左：业务类型统计表
    type_lf = tk.LabelFrame(middle_frame, text=' 业务类型统计 ',
                            font=('SimHei', 11, 'bold'), bg='#FFFFFF')
    type_lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    type_columns = ('type_name', 'count', 'quantity', 'percentage')
    type_headers = {
        'type_name': '业务类型',
        'count': '出库次数',
        'quantity': '出库数量',
        'percentage': '占比%'
    }
    type_tree = _create_treeview_table(type_lf, type_columns, type_headers, height=4)
    
    ty_vsb, ty_hsb = _setup_table_scrollbar(type_tree, type_lf)
    ty_vsb.pack(side=tk.RIGHT, fill=tk.Y)
    ty_hsb.pack(side=tk.BOTTOM, fill=tk.X)
    type_tree.pack(fill=tk.BOTH, expand=True)

    def _refresh_type_table(start_date, end_date):
        """刷新业务类型统计表"""
        for item in type_tree.get_children():
            type_tree.delete(item)
        
        data = service.get_outbound_type_breakdown(start_date, end_date)
        types_list = data['types']
        
        for t in types_list:
            type_tree.insert('', tk.END, values=(
                t['type_name'], t['count'], t['quantity'], f"{t['percentage']}%"
            ))
        
        if not types_list:
            type_tree.insert('', tk.END, values=('暂无出库记录', '-', '-', '-'))

    # 中部右：趋势预测面板
    forecast_lf = tk.LabelFrame(middle_frame, text=' 趋势预测 ',
                                font=('SimHei', 11, 'bold'), bg='#FFFFFF')
    forecast_lf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    forecast_inner = tk.Frame(forecast_lf, bg='#FFFFFF')
    forecast_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

    # 预测周期选择
    period_frame = tk.Frame(forecast_inner, bg='#FFFFFF')
    period_frame.pack(fill=tk.X, pady=(0, 8))
    
    tk.Label(period_frame, text='预测周期:', font=('SimHei', 9),
            bg='#FFFFFF').pack(side=tk.LEFT)
    
    period_var = tk.StringVar(value='7')
    period_combo = ttk.Combobox(period_frame, textvariable=period_var,
                               values=['7', '15', '30'], state='readonly', 
                               width=5, font=('SimHei', 9))
    period_combo.pack(side=tk.LEFT, padx=(5, 10))
    
    tk.Label(period_frame, text='天', font=('SimHei', 9),
            bg='#FFFFFF').pack(side=tk.LEFT)
    
    # 预测数据表
    fcst_columns = ('date', 'predicted_stock', 'daily_change', 'trend')
    fcst_headers = {
        'date': '日期',
        'predicted_stock': '预测库存',
        'daily_change': '日变动',
        'trend': '趋势'
    }
    fcst_tree = _create_treeview_table(forecast_inner, fcst_columns, fcst_headers, height=5)
    
    fc_vsb, fc_hsb = _setup_table_scrollbar(fcst_tree, forecast_inner)
    fc_vsb.pack(side=tk.RIGHT, fill=tk.Y)
    fc_hsb.pack(side=tk.BOTTOM, fill=tk.X)
    fcst_tree.pack(fill=tk.BOTH, expand=True)

    # 指标摘要卡片区
    indicators_frame = tk.Frame(forecast_inner, bg='#FFFFFF')
    indicators_frame.pack(fill=tk.X, pady=(8, 0))

    ind_labels = ['日均消耗', '断货预估', '周转天数']
    ind_values_vars = [tk.StringVar(value='-'), tk.StringVar(value='-'), tk.StringVar(value='-')]
    
    for i, (lbl, var) in enumerate(zip(ind_labels, ind_values_vars)):
        card = tk.Frame(indicators_frame, bg='#E8F4F8', padx=10, pady=6)
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0 if i==0 else 5, 0))
        
        tk.Label(card, text=lbl, font=('SimHei', 8),
                fg='#666666', bg='#E8F4F8').pack()
        tk.Label(card, textvariable=var, font=('SimHei', 14, 'bold'),
                fg='#1E90FF', bg='#E8F4F8').pack()

    def _refresh_forecast_panel():
        """刷新趋势预测面板"""
        days = int(period_var.get())
        forecast_data = service.get_inventory_forecast(days)
        
        # 清空预测表
        for item in fcst_tree.get_children():
            fcst_tree.delete(item)
        
        # 插入预测数据
        for row in forecast_data['forecast_table'][:10]:  # 最多显示10行
            trend = row['trend']
            trend_tag = 'trend_up' if '↑' in trend else ('trend_down' if '↓' in trend else 'trend_stable')
            
            fcst_tree.insert('', tk.END, values=(
                row['date'], int(row['predicted_stock']), 
                row['daily_change'], trend
            ), tags=(trend_tag,))
        
        # 更新指标卡片
        indicators = forecast_data['indicators']
        ind_values_vars[0].set(f"{indicators.get('avg_daily_consumption', '-')}")
        ind_values_vars[1].set(indicators.get('estimated_stockout_date') or '充足')
        ind_values_vars[2].set(f"{indicators.get('inventory_turnover_days', '-')}" or '-')
        
        # 如果是模拟模式且无数据，显示说明
        if forecast_data['is_simulation'] and not forecast_data['forecast_table']:
            fcst_tree.insert('', tk.END, values=('暂无历史数据', '', '', ''), tags=('odd',))
    
    # 刷新按钮（放在函数定义之后）
    refresh_btn = tk.Button(period_frame, text='刷新', 
                           command=_refresh_forecast_panel,
                           font=('SimHei', 9), bg='#17A2B8', fg='white', bd=0)
    refresh_btn.pack(side=tk.LEFT, padx=10)

    # ===== 下部：出入库流水明细表 =====
    timeline_lf = tk.LabelFrame(content_frame, text=' 出入库流水明细（按时间倒序） ',
                                font=('SimHei', 11, 'bold'), bg='#FFFFFF')
    timeline_lf.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 15))

    tl_columns = ('time', 'flow_type', 'name', 'batch_number', 'quantity', 
                 'business_type', 'operator')
    tl_headers = {
        'time': '时间',
        'flow_type': '类型',
        'name': '疫苗名称',
        'batch_number': '批次号',
        'quantity': '数量',
        'business_type': '业务类型',
        'operator': '操作人'
    }
    tl_tree = _create_treeview_table(timeline_lf, tl_columns, tl_headers, height=8)
    
    tl_vsb, tl_hsb = _setup_table_scrollbar(tl_tree, timeline_lf)
    tl_vsb.pack(side=tk.RIGHT, fill=tk.Y)
    tl_hsb.pack(side=tk.BOTTOM, fill=tk.X)
    tl_tree.pack(fill=tk.BOTH, expand=True)

    def _refresh_timeline_table(start_date, end_date):
        """刷新流水明细表"""
        for item in tl_tree.get_children():
            tl_tree.delete(item)
        
        data = service.get_merged_flow_timeline(start_date, end_date, limit=50)
        records = data['records']
        
        for r in records:
            qty = r['quantity']
            flow_type = r['flow_type']
            type_icon = '📥 入库' if flow_type == 'inbound' else '📤 出库'
            qty_str = f'+{abs(qty)}' if flow_type == 'inbound' else str(qty)
            
            tl_tree.insert('', tk.END, values=(
                r['time'][:16], type_icon, r['name'], r['batch_number'],
                qty_str, r['business_type'], r['operator']
            ))
        
        # 显示更多提示
        if data['has_more']:
            tl_tree.insert('', tk.END, values=(
                f'... 还有 {data["total_count"]-50} 条记录未显示', '', '', '', '', '', ''
            ), tags=('odd',))

    # 初始加载
    refresh_all_tables()

    # 绑定滚动事件
    def on_mousewheel(event):
        content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    content_canvas.bind_all("<MouseWheel>", on_mousewheel)

    content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
