# 业务管理相关页面

import tkinter as tk
from tkinter import messagebox
import datetime


def render_outbound(parent, service):
    # 出库登记页面

    from tkinter import ttk
    
    # ========== 颜色常量 ==========
    C_PRIMARY = '#1E90FF'
    C_ACCENT = '#FF9900'
    C_SUCCESS = '#00CC00'
    C_ERROR = '#FF6347'
    C_HEADER = '#2C3E50'
    C_BG_LIGHT = '#F5F5F5'
    C_HOVER = '#E3F2FD'
    C_WHITE = '#FFFFFF'
    
    # 出库类型映射
    TYPE_MAP = {
        'allocation': '调拨出库',
        'vaccination': '接种出库',
        'scrap': '报废出库',
        'return': '退回出库'
    }
    STATUS_MAP = {
        'completed': ('已完成', C_SUCCESS),
        'pending_review': ('待复核', C_ACCENT),
        'rejected': ('已驳回', C_ERROR)
    }
    
    # 运输方式选项
    TRANSPORT_OPTIONS = ['冷藏车运输', '冷链箱转运', '常温运输', '航空冷链', '铁路冷链']
    
    # ==================== 主容器：左右分栏 ====================
    main_container = tk.Frame(parent, bg=C_WHITE)
    main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    
    # 左侧面板 - 数据列表区 (60%)
    left_panel = tk.Frame(main_container, bg=C_WHITE)
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
    
    # 右侧面板 - 操作区 (40%)
    right_panel = tk.Frame(main_container, bg=C_WHITE, width=480)
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(8, 0))
    right_panel.pack_propagate(False)
    
    # ==================== 左侧面板：查询条件 + 记录表格 ====================
    
    # --- 查询条件区域 ---
    filter_frame = tk.LabelFrame(left_panel, text=' 查询条件 ', 
                                  font=('SimHei', 11, 'bold'), fg=C_HEADER,
                                  bg=C_WHITE, padx=10, pady=8)
    filter_frame.pack(fill=tk.X, pady=(0, 8))
    
    # 第一行：疫苗名称 + 批次号
    row1 = tk.Frame(filter_frame, bg=C_WHITE)
    row1.pack(fill=tk.X, pady=2)
    
    tk.Label(row1, text='疫苗名称:', font=('SimHei', 10), bg=C_WHITE).pack(side=tk.LEFT)
    filter_vaccine_var = tk.StringVar()
    vaccine_name_list = sorted(list(set(v['name'] for v in service.vaccines)))
    filter_vaccine_combo = ttk.Combobox(row1, textvariable=filter_vaccine_var,
                                        values=['全部'] + vaccine_name_list,
                                        width=16, font=('SimHei', 10))
    filter_vaccine_combo.pack(side=tk.LEFT, padx=(4, 15))
    filter_vaccine_combo.current(0) if vaccine_name_list else None
    
    tk.Label(row1, text='批次号:', font=('SimHei', 10), bg=C_WHITE).pack(side=tk.LEFT)
    filter_batch_var = tk.StringVar()
    filter_batch_entry = tk.Entry(row1, textvariable=filter_batch_var,
                                   font=('SimHei', 10), width=14)
    filter_batch_entry.pack(side=tk.LEFT, padx=4)
    
    # 第二行：日期范围 + 出库类型
    row2 = tk.Frame(filter_frame, bg=C_WHITE)
    row2.pack(fill=tk.X, pady=2)
    
    tk.Label(row2, text='起始日期:', font=('SimHei', 10), bg=C_WHITE).pack(side=tk.LEFT)
    filter_start_var = tk.StringVar()
    filter_start_entry = tk.Entry(row2, textvariable=filter_start_var,
                                   font=('SimHei', 10), width=12)
    filter_start_entry.pack(side=tk.LEFT, padx=4)
    filter_start_entry.insert(0, '')
    
    tk.Label(row2, text='结束:', font=('SimHei', 10), bg=C_WHITE).pack(side=tk.LEFT, padx=(8, 0))
    filter_end_var = tk.StringVar()
    filter_end_entry = tk.Entry(row2, textvariable=filter_end_var,
                                 font=('SimHei', 10), width=12)
    filter_end_entry.pack(side=tk.LEFT, padx=4)
    filter_end_entry.insert(0, datetime.datetime.now().strftime('%Y-%m-%d'))
    
    tk.Label(row2, text='  出库类型:', font=('SimHei', 10), bg=C_WHITE).pack(side=tk.LEFT, padx=(15, 0))
    filter_type_var = tk.StringVar(value='全部')
    type_options = ['全部', 'allocation', 'vaccination', 'scrap', 'return']
    for topt in type_options:
        rb = tk.Radiobutton(row2, text=TYPE_MAP.get(topt, topt), variable=filter_type_var,
                           value=topt, font=('SimHei', 9), bg=C_WHITE, selectcolor=C_WHITE)
        rb.pack(side=tk.LEFT, padx=3)
    
    # 查询按钮行
    btn_row = tk.Frame(filter_frame, bg=C_WHITE)
    btn_row.pack(fill=tk.X, pady=(6, 0))
    
    # 统计标签
    stats_label = tk.Label(btn_row, text='', font=('SimHei', 10, 'bold'),
                           fg=C_HEADER, bg=C_WHITE)
    stats_label.pack(side=tk.LEFT)
    
    tk.Button(btn_row, text='🔍 查询', command=lambda: refresh_record_table(),
              font=('SimHei', 10, 'bold'), bg=C_PRIMARY, fg=C_WHITE,
              bd=0, cursor='hand2', width=8).pack(side=tk.RIGHT, padx=3)
    tk.Button(btn_row, text='🔄 重置', command=lambda: reset_filters(),
              font=('SimHei', 10), bg='#757575', fg=C_WHITE,
              bd=0, cursor='hand2', width=8).pack(side=tk.RIGHT, padx=3)
    
    # --- 出库记录表格（Canvas滚动） ---
    table_container = tk.Frame(left_panel, bg=C_WHITE)
    table_container.pack(fill=tk.BOTH, expand=True)
    
    # 表格标题栏
    header_row = tk.Frame(table_container, bg=C_HEADER, height=32)
    header_row.pack(fill=tk.X)
    header_row.pack_propagate(False)
    
    table_headers = [
        ('出库单号', 120), ('时间', 130), ('疫苗名称', 110), 
        ('领用单位', 100), ('类型', 70), ('数量', 55),
        ('状态', 65), ('操作', 80)
    ]
    for h_text, h_width in table_headers:
        lbl = tk.Label(header_row, text=h_text, font=('SimHei', 10, 'bold'),
                      fg=C_WHITE, bg=C_HEADER, width=h_width//9, anchor='center')
        lbl.pack(side=tk.LEFT, padx=1, pady=4)
    
    # 可滚动表格区域
    canvas_frame = tk.Frame(table_container, bg=C_WHITE)
    canvas_frame.pack(fill=tk.BOTH, expand=True)
    
    table_canvas = tk.Canvas(canvas_frame, bg=C_WHITE, highlightthickness=1,
                             highlightbackground='#DDDDDD')
    scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=table_canvas.yview)
    scrollable_frame = tk.Frame(table_canvas, bg=C_WHITE)
    
    def on_frame_configure(event):
        """更新滚动区域"""
        table_canvas.configure(scrollregion=table_canvas.bbox('all'))

    def on_canvas_configure(event):
        """Canvas 尺寸变化时，同步内部窗口宽度"""
        table_canvas.itemconfig(canvas_window_id, width=event.width)

    scrollable_frame.bind('<Configure>', on_frame_configure)
    table_canvas.bind('<Configure>', on_canvas_configure)
    canvas_window_id = table_canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
    table_canvas.configure(yscrollcommand=scrollbar.set)
    
    # 鼠标滚轮绑定
    def _on_mousewheel(event):
        table_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    table_canvas.bind_all('<MouseWheel>', _on_mousewheel)
    
    table_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # 存储当前选中的记录ID
    selected_record_id = [None]
    
    # ==================== 右侧面板 ====================
    
    # 页面标题
    right_title = tk.Label(right_panel, text='出库操作区',
                           font=('SimHei', 14, 'bold'), fg=C_HEADER, bg=C_WHITE)
    right_title.pack(pady=(0, 10), anchor='w')
    
    # 新增出库按钮
    new_outbound_btn = tk.Button(right_panel, text='➕ 新增出库登记',
                                 font=('SimHei', 12, 'bold'),
                                 bg=C_ACCENT, fg=C_WHITE, bd=0,
                                 cursor='hand2', height=2,
                                 command=lambda: show_form_mode())
    new_outbound_btn.pack(fill=tk.X, pady=(0, 10))
    
    # --- 出库详情卡片容器（默认隐藏）---
    detail_frame = tk.LabelFrame(right_panel, text=' 出库记录详情 ',
                                  font=('SimHei', 11, 'bold'), fg=C_HEADER,
                                  bg=C_WHITE, padx=0, pady=0)
    
    # 可滚动详情容器
    detail_scroll = tk.Canvas(detail_frame, bg='#F8F9FA', highlightthickness=0)
    detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=detail_scroll.yview)
    detail_container = tk.Frame(detail_scroll, bg='#F8F9FA')
    
    detail_container.bind('<Configure>', lambda e: detail_scroll.configure(scrollregion=detail_scroll.bbox('all')))
    detail_scroll_window = detail_scroll.create_window((0, 0), window=detail_container, anchor='nw', width=430)
    
    def _detail_mousewheel(event):
        detail_scroll.yview_scroll(int(-1 * (event.delta / 120)), "units")
    detail_scroll.bind_all('<MouseWheel>', _detail_mousewheel, add='+')
    
    detail_scroll.configure(yscrollcommand=detail_scrollbar.set)
    detail_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # 默认提示
    detail_hint = tk.Label(detail_container,
                            text='💡 点击左侧表格的"查看"按钮\n\n在此处显示出库记录详情',
                            font=('SimHei', 11), fg='#999', bg='#F8F9FA',
                            justify=tk.CENTER)
    detail_hint.pack(expand=True)
    
    detail_widgets = {}
    
    # --- 出库登记表单容器（默认隐藏）---
    form_outer = tk.Frame(right_panel, bg=C_WHITE)
    
    form_scroll = tk.Canvas(form_outer, bg=C_WHITE, highlightthickness=0)
    form_scrollbar = ttk.Scrollbar(form_outer, orient=tk.VERTICAL, command=form_scroll.yview)
    form_inner = tk.Frame(form_scroll, bg=C_WHITE, padx=10, pady=8)
    
    form_inner.bind('<Configure>', lambda e: form_scroll.configure(scrollregion=form_scroll.bbox('all')))
    form_scroll.create_window((0, 0), window=form_inner, anchor='nw', width=450)
    form_scroll.configure(yscrollcommand=form_scrollbar.set)
    
    def _form_mousewheel(event):
        form_scroll.yview_scroll(int(-1 * (event.delta / 120)), "units")
    form_scroll.bind_all('<MouseWheel>', _form_mousewheel, add='+')
    
    # ===== 领用单位选择区 =====
    unit_section = tk.LabelFrame(form_inner, text=' 🏢 领用单位选择 ',
                                  font=('SimHei', 11, 'bold'), fg=C_HEADER,
                                  bg=C_WHITE, padx=8, pady=6)
    unit_section.pack(fill=tk.X, pady=(0, 8))
    
    urow1 = tk.Frame(unit_section, bg=C_WHITE)
    urow1.pack(fill=tk.X, pady=2)
    tk.Label(urow1, text='单位类型:', font=('SimHei', 10), bg=C_WHITE, width=10, anchor='w').pack(side=tk.LEFT)
    unit_type_var = tk.StringVar(value='all')
    
    utype_frame = tk.Frame(urow1, bg=C_WHITE)
    utype_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
    for ut_key, ut_val in [('all', '全部'), ('cdc', '疾控中心'), ('community', '社区'), ('vaccination', '接种点')]:
        rb = tk.Radiobutton(utype_frame, text=ut_val, variable=unit_type_var, value=ut_key,
                           font=('SimHei', 9), bg=C_WHITE, selectcolor=C_WHITE,
                           command=lambda: on_unit_type_change())
        rb.pack(side=tk.LEFT, padx=4)
    
    urow2 = tk.Frame(unit_section, bg=C_WHITE)
    urow2.pack(fill=tk.X, pady=3)
    tk.Label(urow2, text='领用单位:', font=('SimHei', 10), bg=C_WHITE, width=10, anchor='w').pack(side=tk.LEFT)
    unit_combo_var = tk.StringVar()
    unit_combo = ttk.Combobox(urow2, textvariable=unit_combo_var,
                               values=[], width=28, font=('SimHei', 10), state='readonly')
    unit_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    unit_combo.bind('<<ComboboxSelected>>', lambda e: on_unit_selected())
    
    # 联系人自动填充（只读）
    urow3 = tk.Frame(unit_section, bg=C_WHITE)
    urow3.pack(fill=tk.X, pady=2)
    tk.Label(urow3, text='联系人:', font=('SimHei', 10), bg=C_WHITE, width=10, anchor='w').pack(side=tk.LEFT)
    contact_var = tk.StringVar()
    contact_entry = tk.Entry(urow3, textvariable=contact_var, font=('SimHei', 10),
                              state='readonly', width=18, bg='#F0F0F0')
    contact_entry.pack(side=tk.LEFT, padx=4)
    tk.Label(urow3, text='电话:', font=('SimHei', 10), bg=C_WHITE).pack(side=tk.LEFT, padx=(10, 0))
    phone_var = tk.StringVar()
    phone_entry = tk.Entry(urow3, textvariable=phone_var, font=('SimHei', 10),
                           state='readonly', width=16, bg='#F0F0F0')
    phone_entry.pack(side=tk.LEFT, padx=4)
    
    # 资质信息卡片
    qual_frame = tk.Frame(unit_section, bg='#F8F9FA', bd=1, relief='groove')
    qual_frame.pack(fill=tk.X, pady=(6, 0), padx=2)
    qual_title = tk.Label(qual_frame, text='📋 单位资质信息', font=('SimHei', 9, 'bold'),
                          fg=C_HEADER, bg='#F8F9FA', anchor='w')
    qual_title.pack(anchor='w', padx=6, pady=(4, 0))
    qual_info = tk.Label(qual_frame, text='  请先选择领用单位...', font=('SimHei', 9),
                         fg='#999999', bg='#F8F9FA', justify=tk.LEFT, anchor='w')
    qual_info.pack(anchor='w', padx=6, pady=(2, 6))
    
    # ===== 疫苗批次选择区（近效期优先） =====
    vaccine_section = tk.LabelFrame(form_inner, text=' 💉 疫苗批次选择（近效期优先） ',
                                     font=('SimHei', 11, 'bold'), fg=C_HEADER,
                                     bg=C_WHITE, padx=8, pady=6)
    vaccine_section.pack(fill=tk.X, pady=(0, 8))
    
    vrow1 = tk.Frame(vaccine_section, bg=C_WHITE)
    vrow1.pack(fill=tk.X, pady=2)
    tk.Label(vrow1, text='疫苗名称:', font=('SimHei', 10), bg=C_WHITE, width=10, anchor='w').pack(side=tk.LEFT)
    form_vaccine_var = tk.StringVar()
    stock_vaccine_list = sorted(list(set(v['name'] for v in service.vaccines 
                                         if v.get('status') == 'in_stock' and v.get('quantity', 0) > 0)))
    form_vaccine_combo = ttk.Combobox(vrow1, textvariable=form_vaccine_var,
                                       values=stock_vaccine_list, width=26,
                                       font=('SimHei', 10))
    form_vaccine_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    form_vaccine_combo.bind('<<ComboboxSelected>>', lambda e: on_vaccine_selected())
    
    # 近效期优先批次列表（带效期标记）
    vrow2 = tk.Frame(vaccine_section, bg=C_WHITE)
    vrow2.pack(fill=tk.X, pady=3)
    tk.Label(vrow2, text='选择批次:', font=('SimHei', 10), bg=C_WHITE, width=10, anchor='w').pack(side=tk.LEFT)
    batch_combo_var = tk.StringVar()
    batch_combo = ttk.Combobox(vrow2, textvariable=batch_combo_var,
                                values=[], width=36, font=('SimHei', 10), state='readonly')
    batch_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    batch_combo.bind('<<ComboboxSelected>>', lambda e: on_batch_selected())
    
    # 库存与温度带显示
    info_row = tk.Frame(vaccine_section, bg=C_WHITE)
    info_row.pack(fill=tk.X, pady=3)
    
    stock_info_lbl = tk.Label(info_row, text='可用库存: -- 支', font=('SimHei', 10, 'bold'),
                              fg=C_HEADER, bg=C_WHITE, anchor='w')
    stock_info_lbl.pack(side=tk.LEFT)
    
    temp_info_lbl = tk.Label(info_row, text='', font=('SimHei', 10),
                              fg=C_HEADER, bg=C_WHITE, anchor='e')
    temp_info_lbl.pack(side=tk.RIGHT)
    
    # 效期警告提示
    expiry_warn_lbl = tk.Label(vaccine_section, text='', font=('SimHei', 9),
                                bg=C_WHITE, fg=C_ERROR, wraplength=420, justify=tk.LEFT)
    expiry_warn_lbl.pack(anchor='w', pady=(2, 0))
    
    # ===== 出库信息填写区 =====
    outbound_section = tk.LabelFrame(form_inner, text=' 📋 出库信息填写 ',
                                      font=('SimHei', 11, 'bold'), fg=C_HEADER,
                                      bg=C_WHITE, padx=8, pady=6)
    outbound_section.pack(fill=tk.X, pady=(0, 8))
    
    # 出库类型 Radio
    orow1 = tk.Frame(outbound_section, bg=C_WHITE)
    orow1.pack(fill=tk.X, pady=3)
    tk.Label(orow1, text='出库类型:', font=('SimHei', 10), bg=C_WHITE, width=10, anchor='w').pack(side=tk.LEFT)
    outbound_type_var = tk.StringVar(value='allocation')
    otype_frame = tk.Frame(orow1, bg=C_WHITE)
    otype_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
    for ot_key in ['allocation', 'vaccination', 'scrap', 'return']:
        rb = tk.Radiobutton(otype_frame, text=TYPE_MAP[ot_key], variable=outbound_type_var,
                           value=ot_key, font=('SimHei', 9), bg=C_WHITE, selectcolor=C_WHITE,
                           command=lambda: on_type_change())
        rb.pack(side=tk.LEFT, padx=5)
    
    # 出库数量（实时校验）
    orow2 = tk.Frame(outbound_section, bg=C_WHITE)
    orow2.pack(fill=tk.X, pady=3)
    tk.Label(orow2, text='出库数量:', font=('SimHei', 10), bg=C_WHITE, width=10, anchor='w').pack(side=tk.LEFT)
    quantity_var = tk.StringVar()
    qty_entry = tk.Entry(orow2, textvariable=quantity_var, font=('SimHei', 12, 'bold'),
                         width=10)
    qty_entry.pack(side=tk.LEFT, padx=4)
    tk.Label(orow2, text='支', font=('SimHei', 10), bg=C_WHITE).pack(side=tk.LEFT)
    
    # 数量校验结果标签
    qty_validate_lbl = tk.Label(outbound_section, text='', font=('SimHei', 9),
                                 bg=C_WHITE, wraplength=420)
    qty_validate_lbl.pack(anchor='w', pady=(0, 3))
    qty_entry.bind('<KeyRelease>', lambda e: on_quantity_change())
    qty_entry.bind('<FocusOut>', lambda e: on_quantity_change())
    
    # 运输方式 + 启运温度
    orow3 = tk.Frame(outbound_section, bg=C_WHITE)
    orow3.pack(fill=tk.X, pady=3)
    tk.Label(orow3, text='运输方式:', font=('SimHei', 10), bg=C_WHITE, width=10, anchor='w').pack(side=tk.LEFT)
    transport_var = tk.StringVar()
    transport_combo = ttk.Combobox(orow3, textvariable=transport_var,
                                    values=TRANSPORT_OPTIONS, width=14, font=('SimHei', 10))
    transport_combo.pack(side=tk.LEFT, padx=4)
    transport_combo.current(0) if TRANSPORT_OPTIONS else None
    
    tk.Label(orow3, text='  启运温度:', font=('SimHei', 10), bg=C_WHITE).pack(side=tk.LEFT, padx=(12, 0))
    temp_var = tk.StringVar()
    temp_entry = tk.Entry(orow3, textvariable=temp_var, font=('SimHei', 10), width=6)
    temp_entry.pack(side=tk.LEFT, padx=4)
    tk.Label(orow3, text='℃', font=('SimHei', 10), bg=C_WHITE).pack(side=tk.LEFT)
    
    # 复核人
    orow4 = tk.Frame(outbound_section, bg=C_WHITE)
    orow4.pack(fill=tk.X, pady=3)
    tk.Label(orow4, text='复核人:', font=('SimHei', 10), bg=C_WHITE, width=10, anchor='w').pack(side=tk.LEFT)
    reviewer_var = tk.StringVar()
    reviewer_entry = tk.Entry(orow4, textvariable=reviewer_var, font=('SimHei', 10), width=20)
    reviewer_entry.pack(side=tk.LEFT, padx=4)
    
    # 上传国家平台
    orow5 = tk.Frame(outbound_section, bg=C_WHITE)
    orow5.pack(fill=tk.X, pady=3)
    tk.Label(orow5, text='上传国家平台:', font=('SimHei', 10), bg=C_WHITE, width=10, anchor='w').pack(side=tk.LEFT)
    upload_var = tk.BooleanVar(value=True)
    tk.Checkbutton(orow5, text='是，同步上报至国家免疫规划信息系统',
                   variable=upload_var, font=('SimHei', 10),
                   bg=C_WHITE, selectcolor=C_WHITE, activebackground=C_WHITE).pack(side=tk.LEFT)
    
    # 备注（报废/退回时必填原因）
    remark_row = tk.Frame(outbound_section, bg=C_WHITE)
    remark_row.pack(fill=tk.X, pady=3)
    tk.Label(remark_row, text='备注:', font=('SimHei', 10), bg=C_WHITE, width=10, anchor='w').pack(side=tk.LEFT)
    remark_var = tk.StringVar()
    remark_text = tk.Text(remark_row, font=('SimHei', 10), height=3, width=38, bd=1, relief='solid')
    remark_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
    
    # 退回出库时的关联订单号输入（默认隐藏）
    related_order_row = tk.Frame(outbound_section, bg=C_WHITE)
    tk.Label(related_order_row, text='*原入库单号:', font=('SimHei', 10), bg=C_WHITE,
             width=10, anchor='w', fg=C_ERROR).pack(side=tk.LEFT)
    related_order_var = tk.StringVar()
    related_order_entry = tk.Entry(related_order_row, textvariable=related_order_var,
                                    font=('SimHei', 10), width=24)
    related_order_entry.pack(side=tk.LEFT, padx=4)
    
    # 动态字段提示
    type_hint_lbl = tk.Label(outbound_section, text='', font=('SimHei', 9),
                              fg=C_ACCENT, bg=C_WHITE, wraplength=420)
    type_hint_lbl.pack(anchor='w', pady=(4, 0))
    
    # 提交按钮行
    submit_row = tk.Frame(form_inner, bg=C_WHITE)
    submit_row.pack(fill=tk.X, pady=(10, 5))
    
    submit_btn = tk.Button(submit_row, text='✅ 提交出库登记',
                           font=('SimHei', 13, 'bold'),
                           bg=C_SUCCESS, fg=C_WHITE, bd=0, cursor='hand2',
                           height=2, width=18, command=lambda: submit_outbound())
    submit_btn.pack(side=tk.LEFT, padx=(0, 8))
    
    reset_btn = tk.Button(submit_row, text='重置表单',
                          font=('SimHei', 11),
                          bg='#757575', fg=C_WHITE, bd=0, cursor='hand2',
                          height=2, width=12, command=lambda: reset_form())
    reset_btn.pack(side=tk.LEFT)
    
    # 全局状态变量
    current_mode = ['detail']  # 'detail' 或 'form'
    selected_batch_data = [None]  # 当前选中的批次数据字典
    
    # ==================== 核心业务函数 ====================
    
    def show_form_mode():
        """切换到表单模式"""
        current_mode[0] = 'form'
        new_outbound_btn.pack_forget()
        form_outer.pack(fill=tk.BOTH, expand=True)
        form_scroll.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        form_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        detail_frame.pack_forget()
        # 初始化下拉框数据
        on_unit_type_change()
        reset_form()
    
    def show_detail_mode():
        """切换到详情模式"""
        current_mode[0] = 'detail'
        form_outer.pack_forget()
        detail_frame.pack(fill=tk.BOTH, expand=True)
        if not new_outbound_btn.winfo_ismapped():
            new_outbound_btn.pack(fill=tk.X, pady=(0, 10))
    
    def on_unit_type_change():
        """单位类型改变时更新单位列表"""
        utype = unit_type_var.get()
        units = service.get_recipient_units(utype if utype != 'all' else None)
        unit_names = [(f"{u['id']}|{u['name']}", u['name']) for u in units]
        unit_combo['values'] = [x[1] for x in unit_names]
        if unit_names:
            unit_combo.current(0)
            on_unit_selected()
        else:
            unit_combo_var.set('')
            contact_var.set('')
            phone_var.set('')
            qual_info.config(text='  该类型下暂无可用单位', fg='#999999')
    
    def on_unit_selected():
        """选择单位后填充联系人和资质信息"""
        sel = unit_combo_var.get()
        if not sel:
            return
        # 通过名称查找单位
        units = service.get_recipient_units(unit_type_var.get() if unit_type_var.get() != 'all' else None)
        unit = None
        for u in units:
            if u['name'] == sel:
                unit = u
                break
        if not unit:
            return
        
        contact_var.set(unit.get('contact_person', ''))
        phone_var.set(unit.get('contact_phone', ''))
        
        # 更新资质信息卡片
        qstatus = unit.get('qualification_status', 'unknown')
        qexp = unit.get('qual_expiry_date', '-')
        qno = unit.get('qualification_no', '-')
        
        status_icon = '🟢' if qstatus == 'valid' else ('🟡' if qstatus == 'pending' else '🔴')
        status_text = '有效' if qstatus == 'valid' else ('待审核' if qstatus == 'pending' else '已过期')
        status_color = C_SUCCESS if qstatus == 'valid' else (C_ACCENT if qstatus == 'pending' else C_ERROR)
        
        qual_text = (
            f"  证书编号: {qno}\n"
            f"  有效期至: {qexp}  {status_icon}{status_text}\n"
            f"  联系人: {unit.get('contact_person', '-')}  "
            f"{unit.get('contact_phone', '-')}\n"
            f"  地址: {unit.get('address', '-')}"
        )
        qual_info.config(text=qual_text, fg=status_color)
    
    def on_vaccine_selected():
        """选择疫苗后加载近效期优先排序的批次列表"""
        vname = form_vaccine_var.get()
        batch_combo_var.set('')
        selected_batch_data[0] = None
        stock_info_lbl.config(text='可用库存: -- 支')
        temp_info_lbl.config(text='')
        expiry_warn_lbl.config(text='')
        qty_validate_lbl.config(text='')
        
        if not vname:
            batch_combo['values'] = []
            return
        
        batches = service.get_fefo_vaccine_batches(vname)
        if not batches:
            batch_combo['values'] = []
            return
        
        # 构建带效期标记的显示文本和内部数据映射
        display_list = []
        batch_map = {}
        for b in batches:
            label = b.get('expiry_label', '')
            display_text = (
                f"{b['name']} | {b.get('batch_number', '-')} | "
                f"{b.get('quantity', 0)}支 | 到期:{b.get('expiry_date', '-')} | {label}"
            )
            display_list.append(display_text)
            batch_map[display_text] = b
        
        # 将映射保存到 on_batch_selected 函数属性上，避免全局变量污染
        on_batch_selected._batch_map = batch_map
        
        batch_combo['values'] = display_list
        if display_list:
            batch_combo.current(0)
            on_batch_selected()
    
    def on_batch_selected():
        """选择批次后更新库存和温度信息"""
        sel = batch_combo_var.get()
        batch_map = getattr(on_batch_selected, '_batch_map', {})
        if not sel or not batch_map:
            return
        
        batch = batch_map.get(sel)
        if not batch:
            return
        
        selected_batch_data[0] = batch
        qty = batch.get('quantity', 0)
        stock_info_lbl.config(text=f'可用库存: {qty} 支')
        
        # 温度带信息
        temp_req = batch.get('temp_requirement', {})
        temp_check = service.check_temperature_compliance(batch.get('id'))
        
        temp_display = f"存储要求: {temp_req.get('display', '?')}"
        if temp_check.get('compliant'):
            temp_info_lbl.config(text=f'{temp_display} ✅', fg=C_SUCCESS)
        else:
            temp_info_lbl.config(text=f'{temp_display} ❌', fg=C_ERROR)
            expiry_warn_lbl.config(
                text=f"⚠️ 温度带校验未通过: {temp_check.get('message', '')}",
                fg=C_ERROR
            )
        
        # 效期警告
        estatus = batch.get('expiry_status', '')
        days = batch.get('days_to_expiry', 999)
        if estatus == 'critical':
            expiry_warn_lbl.config(
                text=f"⚠️ 该批次为近效期疫苗！仅剩 {days} 天到期，请优先使用",
                fg=C_ERROR
            )
        elif estatus == 'warning':
            expiry_warn_lbl.config(
                text=f"⏰ 该批次将在 {days} 天内到期，建议尽快使用",
                fg=C_ACCENT
            )
        else:
            expiry_warn_lbl.config(text='')
    
    def on_quantity_change():
        """数量变化时实时校验库存"""
        qty_str = quantity_var.get().strip()
        if not qty_str:
            qty_validate_lbl.config(text='')
            return
        
        try:
            qty = int(qty_str)
        except ValueError:
            qty_validate_lbl.config(text='❌ 请输入有效数字', fg=C_ERROR)
            return
        
        batch = selected_batch_data[0]
        if not batch:
            qty_validate_lbl.config(text='请先选择疫苗批次', fg=C_ACCENT)
            return
        
        valid, stock, msg = service.validate_outbound_quantity(batch.get('id'), qty)
        if valid:
            qty_validate_lbl.config(text=msg, fg=C_SUCCESS)
            qty_entry.config(fg=C_HEADER)
        else:
            qty_validate_lbl.config(text=msg, fg=C_ERROR)
            qty_entry.config(fg=C_ERROR)
    
    def on_type_change():
        """出库类型切换时动态显隐字段"""
        otype = outbound_type_var.get()
        
        # 报废出库：需要显示原因必填提示
        # 退回出库：需要显示原入库单号字段
        if otype == 'return':
            related_order_row.pack(fill=tk.X, pady=3)
            type_hint_lbl.config(text='* 退回出库需填写原入库单号及退回原因', fg=C_ERROR)
        elif otype == 'scrap':
            related_order_row.pack_forget()
            type_hint_lbl.config(text='* 报废出库需在备注中填写详细报废原因（至少5字）', fg=C_ERROR)
        elif otype == 'vaccination':
            related_order_row.pack_forget()
            type_hint_lbl.config(text='💡 接种出库建议选择"接种点"类型领用单位', fg=C_ACCENT)
        else:
            related_order_row.pack_forget()
            type_hint_lbl.config(text='')
    
    def reset_form():
        """重置所有表单字段"""
        unit_type_var.set('all')
        unit_combo_var.set('')
        contact_var.set('')
        phone_var.set('')
        qual_info.config(text='  请先选择领用单位...', fg='#999999')
        form_vaccine_var.set('')
        batch_combo_var.set('')
        selected_batch_data[0] = None
        stock_info_lbl.config(text='可用库存: -- 支')
        temp_info_lbl.config(text='')
        expiry_warn_lbl.config(text='')
        outbound_type_var.set('allocation')
        quantity_var.set('')
        qty_validate_lbl.config(text='')
        transport_var.set(TRANSPORT_OPTIONS[0] if TRANSPORT_OPTIONS else '')
        temp_var.set('')
        reviewer_var.set('')
        upload_var.set(True)
        remark_var.set('')
        remark_text.delete('1.0', tk.END)
        related_order_var.set('')
        related_order_row.pack_forget()
        type_hint_lbl.config(text='')
        on_unit_type_change()
    
    def submit_outbound():
        """提交出库登记 - 完整校验链"""
        # 1. 基础字段校验
        if not unit_combo_var.get():
            messagebox.showerror('校验失败', '❌ 请选择领用单位')
            return
        if not form_vaccine_var.get():
            messagebox.showerror('校验失败', '❌ 请选择疫苗名称')
            return
        if not batch_combo_var.get() or not selected_batch_data[0]:
            messagebox.showerror('校验失败', '❌ 请选择出库批次')
            return
        
        qty_str = quantity_var.get().strip()
        if not qty_str:
            messagebox.showerror('校验失败', '❌ 请填写出库数量')
            return
        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror('校验失败', '❌ 出库数量必须是大于0的整数')
            return
        
        if not reviewer_var.get().strip():
            messagebox.showerror('校验失败', '❌ 请填写复核人姓名')
            return
        
        # 2. 库存校验
        batch = selected_batch_data[0]
        valid, stock, msg = service.validate_outbound_quantity(batch.get('id'), qty)
        if not valid:
            messagebox.showerror('库存校验失败', msg)
            return
        
        # 3. 类型专项校验
        otype = outbound_type_var.get()
        remark_text_content = remark_text.get('1.0', tk.END).strip()
        extra_fields = {
            'remark': remark_text_content,
            'recipient_unit_id': _extract_unit_id(),
            'related_order_id': related_order_var.get().strip()
        }
        type_valid, type_msg = service.validate_outbound_by_type(otype, extra_fields)
        if not type_valid:
            messagebox.showerror(f'{TYPE_MAP.get(otype, "")}校验失败', type_msg)
            return
        
        # 4. 构造出库数据并调用服务层
        unit_id = _extract_unit_id()
        outbound_data = {
            'vaccine_id': batch.get('id'),
            'recipient_unit_id': unit_id,
            'outbound_type': otype,
            'quantity': qty,
            'transport_method': transport_var.get(),
            'departure_temp': temp_var.get(),
            'reviewer': reviewer_var.get().strip(),
            'uploaded_to_national': upload_var.get(),
            'remark': remark_text_content,
            'related_order_id': related_order_var.get().strip() if otype == 'return' else '',
            'operator': (service.current_user or {}).get('username', 'system')
        }
        
        success, msg, record = service.create_outbound_record(outbound_data)
        
        if success:
            messagebox.showinfo('✅ 出库成功', f'{msg}\n\n单号: {record["outbound_id"]}')
            
            # 刷新记录表格
            refresh_record_table()
            
            # 重置表单并切回详情模式
            reset_form()
            show_detail_mode()
            
            # 显示刚创建的记录详情
            if record:
                show_record_detail(record)
        else:
            messagebox.showerror('出库失败', msg)
    
    def _extract_unit_id():
        """从单位名称中提取单位ID"""
        sel = unit_combo_var.get()
        units = service.get_recipient_units(unit_type_var.get() if unit_type_var.get() != 'all' else None)
        for u in units:
            if u['name'] == sel:
                return u['id']
        return None
    
    # ==================== 表格相关函数 ====================
    
    def build_table_row(record, index):
        """构建一条表格行"""
        row_bg = C_BG_LIGHT if index % 2 == 0 else C_WHITE
        
        row_frame = tk.Frame(scrollable_frame, bg=row_bg, pady=2)
        row_frame.pack(fill=tk.X)
        
        # 绑定悬停高亮
        def on_enter(e):
            e.widget.config(bg=C_HOVER)
            for child in e.widget.winfo_children():
                try:
                    if not isinstance(child, tk.Button):
                        child.config(bg=C_HOVER)
                except tk.TclError:
                    pass
        def on_leave(e):
            e.widget.config(bg=row_bg)
            for child in e.widget.winfo_children():
                try:
                    if not isinstance(child, tk.Button):
                        child.config(bg=row_bg)
                except tk.TclError:
                    pass
        
        row_frame.bind('<Enter>', on_enter)
        row_frame.bind('<Leave>', on_leave)
        
        oid = record.get('outbound_id', '')
        otime = record.get('outbound_time', '')[:16]
        vname = record.get('vaccine_name', '')
        rname = record.get('recipient_unit_name', '')[:8]
        otype = record.get('outbound_type', '')
        qty = record.get('quantity', 0)
        status = record.get('status', 'completed')
        
        # 各列单元格
        cells = [
            (oid[:14], 120), (otime, 130), (vname[:10], 110),
            (rname, 100), (TYPE_MAP.get(otype, otype)[:4], 70),
            (str(qty), 55)
        ]
        
        for ctext, cwidth in cells:
            lbl = tk.Label(row_frame, text=ctext, font=('SimHei', 9),
                          fg='#333333', bg=row_bg, width=cwidth//9,
                          anchor='center')
            lbl.pack(side=tk.LEFT, padx=1)
            lbl.bind('<Enter>', on_enter)
            lbl.bind('<Leave>', on_leave)
        
        # 状态列（颜色编码）
        s_text, s_color = STATUS_MAP.get(status, (status, '#666666'))
        status_lbl = tk.Label(row_frame, text=s_text, font=('SimHei', 9, 'bold'),
                              fg=s_color, bg=row_bg, width=7, anchor='center')
        status_lbl.pack(side=tk.LEFT, padx=1)
        status_lbl.bind('<Enter>', on_enter)
        status_lbl.bind('<Leave>', on_leave)
        
        # 操作列：查看按钮
        view_btn = tk.Button(row_frame, text='查看', font=('SimHei', 8),
                             bg=C_PRIMARY, fg='white', bd=0, cursor='hand2',
                             width=6, command=lambda rid=oid: on_view_record(rid))
        view_btn.pack(side=tk.LEFT, padx=2)
    
    def on_view_record(outbound_id):
        """点击查看按钮 -> 显示详情"""
        record = service.get_outbound_record_by_id(outbound_id)
        if record:
            selected_record_id[0] = outbound_id
            show_record_detail(record)
            show_detail_mode()
    
    def show_record_detail(record):
        """在右侧详情卡片中展示出库记录完整信息（卡片式布局）"""
        # 清除旧内容
        for widget in detail_container.winfo_children():
            widget.destroy()
        detail_widgets.clear()
        
        # 标题栏
        title_bar = tk.Frame(detail_container, bg=C_PRIMARY)
        title_bar.pack(fill=tk.X, pady=(0, 12))
        
        oid = record.get('outbound_id', '-')
        tk.Label(title_bar, text=f"📋  {oid}",
                 font=('SimHei', 13, 'bold'), fg='white', bg=C_PRIMARY).pack(pady=8)
        
        # 信息卡片
        info_card = tk.Frame(detail_container, bg=C_WHITE, relief=tk.RAISED, bd=1)
        info_card.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # 分隔线组件
        def add_section(title_text, info_frame):
            sep = tk.Frame(info_frame, bg='#EEEEEE', height=1)
            sep.pack(fill=tk.X, padx=12, pady=(6, 2))
            sec_lbl = tk.Label(info_frame, text=title_text, font=('SimHei', 9, 'bold'),
                              fg=C_PRIMARY, bg=C_WHITE, anchor='w')
            sec_lbl.pack(fill=tk.X, padx=12, pady=(0, 2))
        
        def add_field(label, value, info_frame):
            field_row = tk.Frame(info_frame, bg=C_WHITE)
            field_row.pack(fill=tk.X, padx=12, pady=3)
            
            lbl = tk.Label(field_row, text=label.strip(), font=('SimHei', 10),
                          fg='#555', bg=C_WHITE, anchor='w', width=11)
            lbl.pack(side=tk.LEFT)
            
            # 颜色逻辑：状态、效期等
            color = '#1a1a1a'
            sv = str(value)
            if '状态' in label:
                if '已完成' in sv:
                    color = C_SUCCESS
                elif '待复核' in sv:
                    color = C_ACCENT
                elif '已驳回' in sv:
                    color = C_ERROR
            elif '有效期' in label:
                try:
                    expiry = datetime.datetime.strptime(sv[:10], '%Y-%m-%d').date()
                    days_left = (expiry - datetime.date.today()).days
                    if days_left < 0:
                        color = C_ERROR
                    elif days_left <= 30:
                        color = C_ACCENT
                    else:
                        color = C_SUCCESS
                except (ValueError, TypeError):
                    pass
            
            val_lbl = tk.Label(field_row, text=sv[:40], font=('SimHei', 10, 'bold'),
                              fg=color, bg=C_WHITE, anchor='w', wraplength=260)
            val_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
            return val_lbl
        
        # ===== 单据信息 =====
        add_field('📌 出库单号', record.get('outbound_id', '-'), info_card)
        add_field('🕐 出库时间', record.get('outbound_time', '-'), info_card)
        
        # ===== 疫苗信息 =====
        add_section('💉 疫苗信息', info_card)
        add_field('疫苗名称', record.get('vaccine_name', '-'), info_card)
        add_field('批次号', record.get('batch_number', '-'), info_card)
        add_field('生产厂家', record.get('manufacturer', '-'), info_card)
        add_field('有效期至', record.get('vaccine_expiry_date', '-'), info_card)
        add_field('出库数量', f"{record.get('quantity', 0)} 支", info_card)
        
        # ===== 领用单位 =====
        add_section('🏢 领用单位', info_card)
        add_field('单位名称', record.get('recipient_unit_name', '-'), info_card)
        
        # ===== 出库信息 =====
        add_section('📤 出库信息', info_card)
        add_field('出库类型', TYPE_MAP.get(record.get('outbound_type', '-'), record.get('outbound_type', '-')), info_card)
        add_field('运输方式', record.get('transport_method', '-'), info_card)
        add_field('启运温度', f"{record.get('departure_temp', '-')}℃", info_card)
        add_field('复核人', record.get('reviewer', '-'), info_card)
        add_field('操作人', record.get('operator', '-'), info_card)
        
        # ===== 状态与上报 =====
        add_section('📊 状态信息', info_card)
        stxt, _ = STATUS_MAP.get(record.get('status', 'completed'), (record.get('status', '-'), '#666666'))
        add_field('当前状态', stxt, info_card)
        add_field('上传国家平台', '是' if record.get('uploaded_to_national') else '否', info_card)
        
        # 备注
        if record.get('remark'):
            add_section('📝 备注信息', info_card)
            remark_lbl = tk.Label(info_card, text=f"  {record.get('remark', '')}",
                                  font=('SimHei', 9), fg='#555', bg=C_WHITE,
                                  justify=tk.LEFT, wraplength=380, anchor='w')
            remark_lbl.pack(fill=tk.X, padx=12, pady=(2, 6))
        
        # 关联单号
        if record.get('related_order_id'):
            add_field('🔗 关联入库单号', record.get('related_order_id', '-'), info_card)
        
        # ===== 时间记录 =====
        add_section('🕐 时间记录', info_card)
        add_field('创建时间', record.get('create_time', '-'), info_card)
        if record.get('review_time'):
            add_field('复核时间', record.get('review_time', '-'), info_card)
        if record.get('complete_time'):
            add_field('完成时间', record.get('complete_time', '-'), info_card)
        
        # 底部留白
        tk.Frame(info_card, bg=C_WHITE, height=8).pack()
        
        # 强制刷新滚动区域
        detail_container.update_idletasks()
        detail_scroll.itemconfig(detail_scroll_window,
                                 width=detail_container.winfo_reqwidth())
        detail_scroll.configure(scrollregion=detail_scroll.bbox('all'))
    
    def refresh_record_table():
        """刷新出库记录表格"""
        # 清空现有行
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        # 构建筛选条件
        filters = {}
        fv = filter_vaccine_var.get()
        if fv and fv != '全部':
            filters['vaccine_name'] = fv
        fb = filter_batch_var.get().strip()
        if fb:
            filters['batch_number'] = fb
        fs = filter_start_var.get().strip()
        if fs:
            filters['start_date'] = fs
        fe = filter_end_var.get().strip()
        if fe:
            filters['end_date'] = fe
        ft = filter_type_var.get()
        if ft and ft != '全部':
            filters['outbound_type'] = ft
        
        records = service.get_outbound_records(filters)
        
        # 更新统计
        total_qty = sum(r.get('quantity', 0) for r in records)
        stats_label.config(text=f'共 {len(records)} 条记录，合计 {total_qty} 支')
        
        if not records:
            empty_lbl = tk.Label(scrollable_frame, text='  🔍 暂无符合条件的出库记录',
                                 font=('SimHei', 11), fg='#999999', bg=C_WHITE, pady=30)
            empty_lbl.pack()
            return
        
        for idx, rec in enumerate(records):
            build_table_row(rec, idx)
    
    def reset_filters():
        """重置查询条件"""
        filter_vaccine_combo.current(0) if vaccine_name_list else None
        filter_batch_var.set('')
        filter_start_var.set('')
        filter_end_var.set(datetime.datetime.now().strftime('%Y-%m-%d'))
        filter_type_var.set('全部')
        refresh_record_table()
    
    # ==================== 初始化执行 ====================
    
    # 默认显示详情模式
    show_detail_mode()
    
    # 加载初始表格数据
    refresh_record_table()


def render_expiry_remind(parent, service):
    """有效期提醒页面"""
    title = tk.Label(parent, text='有效期提醒',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)
    
    expiring_vaccines = service.get_expiring_vaccines(30)
    
    if not expiring_vaccines:
        tk.Label(parent, text='✅ 暂无即将过期的疫苗',
                font=('SimHei', 14), fg='#00CC00', bg='#FFFFFF').pack(pady=50)
        return
    
    list_frame = tk.Frame(parent, bg='#FFFFFF', padx=40)
    list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    
    for vaccine in expiring_vaccines:
        item_text = f"名称: {vaccine['name']} | 批次: {vaccine.get('batch_number', '-')} | 数量: {vaccine['quantity']}剂 | 有效期: {vaccine['expiry_date']}"
        tk.Label(list_frame, text=item_text, font=('SimHei', 12),
                bg='#FFF3E0', fg='#FF6600').pack(fill=tk.X, pady=2, padx=10)


def render_expiry_handle(parent, service):
    """过期产品处理页面"""
    title = tk.Label(parent, text='过期产品处理',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)
    
    expired_vaccines = service.get_expired_vaccines()
    
    if not expired_vaccines:
        tk.Label(parent, text='✅ 当前没有过期产品',
                font=('SimHei', 14), fg='#00CC00', bg='#FFFFFF').pack(pady=50)
        return
    
    form_frame = tk.Frame(parent, bg='#FFFFFF', padx=40)
    form_frame.pack(pady=10, fill=tk.X)
    
    tk.Label(form_frame, text=f'发现 {len(expired_vaccines)} 条过期记录',
            font=('SimHei', 12), fg='#FF0000', bg='#FFFFFF').pack(anchor=tk.W)
    
    def handle_expired():
        count = service.cancel_expired()
        messagebox.showinfo('成功', f'已标记 {count} 条过期产品')
    
    handle_btn = tk.Button(form_frame, text='标记所有过期产品',
                         command=handle_expired,
                         font=('SimHei', 12), bg='#FF6347', fg='white', width=20)
    handle_btn.pack(pady=20)


def render_inventory_list(parent, service):
    """库存清单页面 — 支持分类别、分厂家筛选"""
    from tkinter import ttk
    
    title = tk.Label(parent, text='库存清单',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)
    
    # ===================== 筛选区域 =====================
    filter_frame = tk.Frame(parent, bg='#FFFFFF')
    filter_frame.pack(fill=tk.X, padx=40, pady=(0, 10))
    
    # 类别下拉框
    tk.Label(filter_frame, text='类别：', font=('SimHei', 10),
             bg='#FFFFFF').pack(side=tk.LEFT)
    categories = sorted(list(set(
        v.get('category', '') for v in (service.vaccines or []) if v.get('category')
    )))
    category_var = tk.StringVar(value='全部')
    category_combo = ttk.Combobox(filter_frame, textvariable=category_var,
                                  values=['全部'] + categories,
                                  font=('SimHei', 10), width=14, state='readonly')
    category_combo.pack(side=tk.LEFT, padx=(0, 15))
    category_combo.current(0)
    
    # 厂家下拉框
    tk.Label(filter_frame, text='厂家：', font=('SimHei', 10),
             bg='#FFFFFF').pack(side=tk.LEFT)
    manufacturers = sorted(list(set(
        v.get('manufacturer', '') for v in (service.vaccines or []) if v.get('manufacturer')
    )))
    manufacturer_var = tk.StringVar(value='全部')
    manufacturer_combo = ttk.Combobox(filter_frame, textvariable=manufacturer_var,
                                      values=['全部'] + manufacturers,
                                      font=('SimHei', 10), width=20, state='readonly')
    manufacturer_combo.pack(side=tk.LEFT, padx=(0, 15))
    manufacturer_combo.current(0)
    
    # 查询 + 重置按钮
    tk.Button(filter_frame, text='查询', command=lambda: _do_filter(),
              font=('SimHei', 10, 'bold'), bg='#1E90FF', fg='white',
              bd=0, cursor='hand2', width=8).pack(side=tk.RIGHT, padx=3)
    tk.Button(filter_frame, text='重置', command=lambda: _reset_filters(),
              font=('SimHei', 10), bg='#757575', fg='white',
              bd=0, cursor='hand2', width=8).pack(side=tk.RIGHT, padx=3)
    
    # 统计标签
    stats_label = tk.Label(parent, text='', font=('SimHei', 9),
                           fg='#666666', bg='#FFFFFF')
    stats_label.pack(anchor=tk.W, padx=40, pady=(0, 5))
    
    # ===================== 表头 =====================
    header_container = tk.Frame(parent, bg='#FFFFFF')
    header_container.pack(fill=tk.X, padx=40)
    
    header_frame = tk.Frame(header_container, bg='#333')
    header_frame.pack(fill=tk.X)
    headers = ['名称', '类别', '厂家', '批号', '数量']
    for h in headers:
        tk.Label(header_frame, text=h, font=('SimHei', 11, 'bold'),
                fg='white', bg='#333', width=15).pack(side=tk.LEFT, padx=2, pady=4)
    
    # ===================== 数据容器（用于动态刷新） =====================
    data_container = tk.Frame(parent, bg='#FFFFFF')
    data_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))
    
    # ===================== 内部函数 =====================
    def _render_table(data_list):
        """渲染库存数据到表格"""
        # 清空现有数据行
        for widget in data_container.winfo_children():
            widget.destroy()
        
        if not data_list:
            tk.Label(data_container, text='暂无符合条件的库存记录',
                    font=('SimHei', 12), fg='#999999', bg='#FFFFFF').pack(pady=30)
            stats_label.config(text='共 0 条记录')
            return
        
        stats_label.config(text=f'共 {len(data_list)} 条库存记录')
        
        for vaccine in data_list:
            row_frame = tk.Frame(data_container, bg='#FFFFFF')
            row_frame.pack(fill=tk.X)
            
            values = [
                vaccine.get('name', '-'),
                vaccine.get('category', '-'),
                vaccine.get('manufacturer', '-'),
                vaccine.get('batch_number', '-'),
                str(vaccine.get('quantity', 0))
            ]
            
            for val in values:
                tk.Label(row_frame, text=val, font=('SimHei', 10),
                        fg='#333', bg='#FFFFFF', width=15).pack(side=tk.LEFT, padx=2, pady=2)
    
    def _do_filter():
        """执行筛选查询"""
        cat = category_var.get()
        mfr = manufacturer_var.get()
        
        cat_param = cat if cat != '全部' else None
        mfr_param = mfr if mfr != '全部' else None
        
        filtered = service.get_stock_list(category=cat_param, manufacturer=mfr_param)
        _render_table(filtered)
    
    def _reset_filters():
        """重置筛选条件"""
        category_var.set('全部')
        manufacturer_var.set('全部')
        _do_filter()
    
    # ===================== 初始加载全部数据 =====================
    _do_filter()


def render_inventory_warning(parent, service):
    """库存预警页面 — 仅低库存预警，展示完整信息"""
    title = tk.Label(parent, text='库存预警',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)
    
    try:
        alerts = service.get_inventory_alerts()
        low_stock = alerts.get('low_stock', [])
        
        if not low_stock:
            tk.Label(parent, text='✅ 库存状态正常',
                    font=('SimHei', 14), fg='#00CC00', bg='#FFFFFF').pack(pady=50)
            return
        
        # 表头
        tk.Label(parent, text=f'⚠️ 库存不足预警 ({len(low_stock)} 项)：',
                font=('SimHei', 13, 'bold'), fg='#FF0000', bg='#FFFFFF'
                ).pack(anchor=tk.W, padx=40, pady=(10, 5))
        
        # 创建表格框架
        table_frame = tk.Frame(parent, bg='#FFFFFF')
        table_frame.pack(fill=tk.X, padx=40, pady=10)
        
        # 表头行
        headers = ['疫苗名称', '类别', '生产厂家', '批号', '数量', '有效期']
        header_frame = tk.Frame(table_frame, bg='#F5F5F5')
        header_frame.pack(fill=tk.X)
        
        col_widths = [18, 14, 24, 14, 6, 12]
        for h, w in zip(headers, col_widths):
            tk.Label(header_frame, text=h, font=('SimHei', 9, 'bold'),
                    fg='#333', bg='#F5F5F5', width=w, anchor='w',
                    relief='solid', bd=1).pack(side=tk.LEFT)
        
        # 数据行
        for v in low_stock:
            row_frame = tk.Frame(table_frame, bg='#FFFFFF')
            row_frame.pack(fill=tk.X)
            
            qty = int(v.get('quantity', 0))
            cells = [
                v.get('name', '-')[:16],
                v.get('category', '-')[:12],
                v.get('manufacturer', '-')[:22],
                v.get('batch_number', '-')[:12],
                f"{qty}剂",
                v.get('expiry_date', '-')
            ]
            
            for c, w in zip(cells, col_widths):
                fg_color = '#FF0000' if qty == 0 else '#333'
                tk.Label(row_frame, text=c, font=('SimHei', 9),
                        fg=fg_color, bg='#FFFFFF', width=w, anchor='w',
                        relief='groove', bd=1).pack(side=tk.LEFT)
                    
    except Exception as e:
        # 页面级错误处理
        error_frame = tk.Frame(parent, bg='#FFF3E0')
        error_frame.pack(fill=tk.X, padx=40, pady=20)
        
        tk.Label(error_frame, 
                text='❌ 加载预警数据失败',
                font=('SimHei', 14), fg='#FF0000', bg='#FFF3E0').pack(pady=10)
        
        tk.Label(error_frame,
                text=f'错误详情：{str(e)}',
                font=('SimHei', 10), fg='#666666', bg='#FFF3E0').pack()
        
        tk.Label(error_frame,
                text='请检查疫苗数据文件或联系管理员',
                font=('SimHei', 10), fg='#999999', bg='#FFF3E0').pack(pady=(0, 10))
