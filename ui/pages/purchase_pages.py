# 采购计划与订单管理相关页面

import tkinter as tk
from tkinter import ttk, messagebox
import datetime


def render_purchase_request(parent, service):
    """按需申购页面 - 左右分栏布局"""

    # ========== 主标题 ==========
    title = tk.Label(parent, text='📋 按需申购',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=(15, 10))

    # ========== 状态说明栏 ==========
    status_bar = tk.Frame(parent, bg='#E8F4FD', padx=15, pady=8)
    status_bar.pack(fill=tk.X, padx=20, pady=(0, 10))

    tk.Label(status_bar,
            text='💡 状态说明：',
            font=('SimHei', 10, 'bold'), fg='#1976D2', bg='#E8F4FD').pack(side=tk.LEFT)
    tk.Label(status_bar,
            text='⏳ 待审批   ✅ 已通过   ❌ 已驳回',
            font=('SimHei', 10), fg='#555', bg='#E8F4FD').pack(side=tk.LEFT, padx=10)

    # ========== 左右分栏主容器 ==========
    main_container = tk.Frame(parent, bg='#FFFFFF')
    main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

    # ---- 左侧：列表区 (占60%) ----
    left_panel = tk.Frame(main_container, bg='#F5F7FA')
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    # 左侧标题栏
    left_header = tk.Frame(left_panel, bg='#2C3E50', height=40)
    left_header.pack(fill=tk.X)
    left_header.pack_propagate(False)

    tk.Label(left_header, text='📋 申购单列表', font=('SimHei', 12, 'bold'),
            fg='white', bg='#2C3E50').pack(side=tk.LEFT, padx=15, pady=8)

    tk.Button(left_header, text='➕ 新增申购', command=lambda: show_add_form(),
             font=('SimHei', 10), bg='#00CC00', fg='white', bd=0,
             cursor='hand2').pack(side=tk.RIGHT, padx=10, pady=6)

    # 表头
    col_headers = ['编号', '疫苗名称', '数量', '申请人', '日期', '状态', '操作']
    col_widths = [6, 14, 5, 8, 10, 7, 5]

    header_row = tk.Frame(left_panel, bg='#34495E')
    header_row.pack(fill=tk.X)

    for h, w in zip(col_headers, col_widths):
        tk.Label(header_row, text=h, font=('SimHei', 9, 'bold'),
                fg='white', bg='#34495E', width=w, anchor='center').pack(side=tk.LEFT, padx=1, pady=4)

    # 数据行容器（带滚动）
    data_canvas = tk.Canvas(left_panel, bg='#F5F7FA', highlightthickness=0)
    data_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=data_canvas.yview)
    data_frame = tk.Frame(data_canvas, bg='#F5F7FA')

    data_frame.bind("<Configure>", lambda e: data_canvas.configure(scrollregion=data_canvas.bbox("all")))
    data_canvas.create_window((0, 0), window=data_frame, anchor="nw", width=left_panel.winfo_reqwidth())
    data_canvas.configure(yscrollcommand=data_scroll.set)

    def on_data_configure(e):
        data_canvas.itemconfig(data_canvas.find_all()[0], width=e.width)
    data_canvas.bind('<Configure>', on_data_configure)

    def _on_mousewheel(e):
        data_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
    data_canvas.bind_all("<MouseWheel>", _on_mousewheel, add='+')

    data_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    data_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 底部计数栏
    count_bar = tk.Frame(left_panel, bg='#ECF0F1', height=32)
    count_bar.pack(fill=tk.X, side=tk.BOTTOM)
    count_bar.pack_propagate(False)
    count_label = tk.Label(count_bar,
                          text=f'共 {len(service.purchase_requests or [])} 条记录',
                          font=('SimHei', 9), fg='#666', bg='#ECF0F1')
    count_label.pack(pady=6)

    # ---- 右侧：动态面板区 (占40%) ----
    right_panel = tk.Frame(main_container, bg='#FAFBFC',
                          width=420, relief=tk.FLAT)
    right_panel.pack(side=tk.RIGHT, fill=tk.Y)
    right_panel.pack_propagate(False)  # 固定宽度

    # 右侧面板标题
    right_title_bar = tk.Frame(right_panel, bg='#1E90FF', height=42)
    right_title_bar.pack(fill=tk.X)
    right_title_bar.pack_propagate(False)

    right_title = tk.Label(right_title_bar, text='📝 详情面板',
                          font=('SimHei', 12, 'bold'), fg='white', bg='#1E90FF')
    right_title.pack(pady=10)

    # 右侧内容容器
    right_content = tk.Frame(right_panel, bg='#FAFBFC')
    right_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    # ========== 状态颜色/文字映射 ==========
    def get_status_color(status):
        mapping = {'approved': '#27AE60', 'pending': '#95A5A6', 'rejected': '#E74C3C'}
        return mapping.get(status, '#333')

    def get_status_text(status):
        return {'pending': '待审批', 'approved': '已通过', 'rejected': '已驳回'}.get(status, status)

    # ========== 右侧面板切换函数 ==========

    def clear_right_panel():
        """清空右侧面板"""
        for w in right_content.winfo_children():
            w.destroy()

    def show_default():
        """显示默认提示"""
        clear_right_panel()
        default_frame = tk.Frame(right_content, bg='#FAFBFC')
        default_frame.place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(default_frame, text='📋', font=('Segoe UI Emoji', 48),
                bg='#FAFBFC').pack(pady=(0, 15))
        tk.Label(default_frame, text='选择一条记录查看详情', font=('SimHei', 11),
                fg='#999', bg='#FAFBFC').pack()
        tk.Label(default_frame, text='或点击「新增申购」按钮', font=('SimHei', 10),
                fg='#BBB', bg='#FAFBFC').pack(pady=(5, 0))
        # 更新标题
        right_title.config(text='📝 详情面板')

    def show_detail(request):
        """在右侧面板显示申购单详情"""
        clear_right_panel()
        right_title.config(text=f'📋 申购单 #{request.get("id", "-")}')

        # 信息卡片
        card = tk.Frame(right_content, bg='#FFFFFF', relief=tk.FLAT, bd=1)
        card.pack(fill=tk.X, pady=(0, 10))

        # 顶部色条
        status = request.get('status', '-')
        color = get_status_color(status)
        top_bar = tk.Frame(card, bg=color, height=4)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)

        info_area = tk.Frame(card, bg='#FFFFFF', padx=20, pady=15)
        info_area.pack(fill=tk.X)

        details = [
            ('申购编号', f"#{request.get('id', '-')}"),
            ('疫苗名称', request.get('vaccine_name', '-')),
            ('申请数量', f"{request.get('quantity', 0)} 剂"),
            ('申请人', request.get('requester', '-') or 'admin'),
            ('申请日期', str(request.get('request_date', '-'))[:16]),
            ('期望交付日', request.get('expected_date', '-') or '未指定'),
            ('申购理由', (request.get('reason', '-') or '-')[:80]),
            ('当前状态', ''),
        ]

        for i, (label, value) in enumerate(details):
            row = tk.Frame(info_area, bg='#FFFFFF')
            row.pack(fill=tk.X, pady=2)

            tk.Label(row, text=label, font=('SimHei', 10), fg='#666',
                    bg='#FFFFFF', anchor='e', width=10).pack(side=tk.LEFT)

            if label == '当前状态':
                stext = get_status_text(status)
                tk.Label(row, text=stext, font=('SimHei', 10, 'bold'),
                        fg=color, bg='#FFFFFF', anchor='w').pack(side=tk.LEFT, padx=10)
            else:
                tk.Label(row, text=value if value else '-', font=('SimHei', 10),
                        fg='#333', bg='#FFFFFF', anchor='w', wraplength=280).pack(side=tk.LEFT, padx=10)

        # 操作按钮区
        btn_area = tk.Frame(right_content, bg='#FAFBFC')
        btn_area.pack(fill=tk.X, pady=10)

        if status == 'pending':
            def approve():
                request['status'] = 'approved'
                service.save_data()
                refresh_table()
                show_detail(request)
                service.log_operation(f'通过申购单 #{request["id"]}')
                messagebox.showinfo('成功', f'申购单 #{request["id"]} 已通过！')

            def reject():
                request['status'] = 'rejected'
                service.save_data()
                refresh_table()
                show_detail(request)
                service.log_operation(f'驳回申购单 #{request["id"]}')
                messagebox.showinfo('已操作', f'申购单 #{request["id"]} 已驳回。')

            tk.Button(btn_area, text='✅ 通过', command=approve,
                     font=('SimHei', 10), bg='#27AE60', fg='white', bd=0,
                     width=10, cursor='hand2').pack(side=tk.LEFT, padx=3)
            tk.Button(btn_area, text='❌ 驳回', command=reject,
                     font=('SimHei', 10), bg='#E74C3C', fg='white', bd=0,
                     width=10, cursor='hand2').pack(side=tk.LEFT, padx=3)

        tk.Button(btn_area, text='返回列表', command=show_default,
                 font=('SimHei', 10), bg='#95A5A6', fg='white', bd=0,
                 width=10, cursor='hand2').pack(side=tk.LEFT, padx=3)

    def show_add_form(edit_request=None):
        """在右侧面板显示新增/编辑表单"""
        clear_right_panel()

        is_edit = edit_request is not None
        right_title.config(text='✏️ 编辑申购单' if is_edit else '📝 新增疫苗申购单')

        form_card = tk.Frame(right_content, bg='#FFFFFF', relief=tk.FLAT, bd=1)
        form_card.pack(fill=tk.X, pady=(0, 10))

        top_bar = tk.Frame(form_card, bg='#1E90FF', height=4)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)

        form = tk.Frame(form_card, bg='#FFFFFF', padx=18, pady=12)
        form.pack(fill=tk.X)

        fields = {}
        configs = [
            ('vaccine_name', '* 疫苗名称', True),
            ('quantity', '* 数量(剂)', False),
            ('requester', '申请人', False),
            ('expected_date', '期望交付日期', False),
            ('reason', '申购理由', True),
        ]

        for i, (key, label, is_combo) in enumerate(configs):
            row = tk.Frame(form, bg='#FFFFFF')
            row.pack(fill=tk.X, pady=4)

            tk.Label(row, text=label, font=('SimHei', 10), fg='#444',
                    bg='#FFFFFF', anchor='e', width=12).pack(side=tk.LEFT)

            if key == 'vaccine_name':
                vaccine_names = list(set(v.get('name', '') for v in service.vaccines if v.get('name')))
                var = tk.StringVar(value=edit_request.get('vaccine_name', '') if is_edit else '')
                fields[key] = var
                combo = ttk.Combobox(row, textvariable=var,
                                    values=[''] + sorted(vaccine_names),
                                    font=('SimHei', 10), width=26)
                combo.pack(side=tk.LEFT, padx=5)
            elif key == 'reason':
                var = tk.Text(form, font=('SimHei', 10), width=28, height=3)
                var.pack(pady=4)
                if is_edit and edit_request.get('reason'):
                    var.insert('1.0', edit_request['reason'])
                fields[key] = var
            else:
                w = 26
                if key == 'quantity':
                    w = 14
                var = tk.StringVar(value=str(edit_request.get(key, '')) if is_edit and edit_request.get(key) else '')
                fields[key] = var
                entry = tk.Entry(row, textvariable=var, font=('SimHei', 10), width=w)
                entry.pack(side=tk.LEFT, padx=5)

        btn_area = tk.Frame(right_content, bg='#FAFBFC')
        btn_area.pack(fill=tk.X, pady=12)

        def submit():
            if isinstance(fields['vaccine_name'], tk.StringVar):
                vname = fields['vaccine_name'].get().strip()
            else:
                vname = ''

            if isinstance(fields['quantity'], tk.StringVar):
                qty_val = fields['quantity'].get().strip()
            else:
                qty_val = ''

            if not vname:
                messagebox.showerror('错误', '请选择或输入疫苗名称！')
                return
            if not qty_val or not qty_val.isdigit() or int(qty_val) <= 0:
                messagebox.showerror('错误', '请填写有效的正整数数量！')
                return

            reason_val = ''
            if isinstance(fields['reason'], tk.Text):
                reason_val = fields['reason'].get('1.0', 'end').strip()
            elif isinstance(fields['reason'], tk.StringVar):
                reason_val = fields['reason'].get().strip()

            requester_val = ''
            if isinstance(fields['requester'], tk.StringVar):
                requester_val = fields['requester'].get().strip()

            expected_val = ''
            if isinstance(fields['expected_date'], tk.StringVar):
                expected_val = fields['expected_date'].get().strip()

            if is_edit:
                # 编辑模式
                edit_request['vaccine_name'] = vname
                edit_request['quantity'] = int(qty_val)
                edit_request['requester'] = requester_val or edit_request.get('requester', 'admin')
                edit_request['expected_date'] = expected_val
                edit_request['reason'] = reason_val
                service.save_data()
                service.log_operation(f'编辑申购单 #{edit_request["id"]}')
                messagebox.showinfo('成功', f'申购单 #{edit_request["id"]} 已更新！')
                refresh_table()
                show_detail(edit_request)
            else:
                # 新增模式
                max_id = max([r.get('id', 0) for r in (service.purchase_requests or [])], default=0)
                new_req = {
                    'id': max_id + 1,
                    'vaccine_name': vname,
                    'quantity': int(qty_val),
                    'requester': requester_val or 'admin',
                    'request_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'expected_date': expected_val,
                    'reason': reason_val,
                    'status': 'pending'
                }
                if not service.purchase_requests:
                    service.purchase_requests = []
                service.purchase_requests.append(new_req)
                service.save_data()
                service.log_operation(f'提交申购单：{vname} - {qty_val}剂')
                messagebox.showinfo('成功', f'申购单已提交！\n等待审批。\n编号: #{new_req["id"]}')
                refresh_table()
                show_default()

        tk.Button(btn_area, text='✅ 提交', command=submit,
                 font=('SimHei', 11, 'bold'), bg='#00CC00', fg='white', bd=0,
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=3)
        tk.Button(btn_area, text='取消', command=show_default,
                 font=('SimHei', 11), bg='#95A5A6', fg='white', bd=0,
                 width=10, cursor='hand2').pack(side=tk.LEFT, padx=3)

    # ========== 左侧表格刷新函数 ==========

    def refresh_table():
        """刷新左侧表格数据"""
        for widget in data_frame.winfo_children():
            widget.destroy()

        requests_list = service.purchase_requests or []
        count_label.config(text=f'共 {len(requests_list)} 条记录')

        if not requests_list:
            empty = tk.Label(data_frame, text='暂无申购记录\n点击右上角「新增申购」添加',
                            font=('SimHei', 11), fg='#AAA', bg='#F5F7FA', justify='center')
            empty.place(relx=0.5, rely=0.4, anchor='center')
        else:
            requests_list.sort(key=lambda x: x.get('request_date', ''), reverse=True)
            for idx, req in enumerate(requests_list[:25]):
                bg = '#FFFFFF' if idx % 2 == 0 else '#EDF2F7'
                row = tk.Frame(data_frame, bg=bg, cursor='hand2')
                row.pack(fill=tk.X)

                # 行悬停效果
                def on_enter(e, r=row):
                    r.config(bg='#D6EAF8')
                    for child in r.winfo_children():
                        if isinstance(child, tk.Label):
                            child.config(bg='#D6EAF8')

                def on_leave(e, r=row, c=bg):
                    r.config(bg=c)
                    for child in r.winfo_children():
                        if isinstance(child, tk.Label):
                            child.config(bg=c)

                row.bind('<Enter>', on_enter)
                row.bind('<Leave>', on_leave)
                row.bind('<Button-1>', lambda e, r=req: show_detail(r))

                values = [
                    f"#{req.get('id', '-')}",
                    str(req.get('vaccine_name', '-'))[:12],
                    f"{req.get('quantity', 0)}",
                    str(req.get('requester', '-') or 'admin')[:7],
                    str(req.get('request_date', '-'))[:10],
                ]

                for val, w in zip(values, col_widths[:-2]):
                    lbl = tk.Label(row, text=val, font=('SimHei', 9),
                                  fg='#333', bg=bg, width=w, anchor='center')
                    lbl.pack(side=tk.LEFT, padx=1, pady=3)

                # 状态
                st = req.get('status', '-')
                tk.Label(row, text=get_status_text(st), font=('SimHei', 9, 'bold'),
                        fg=get_status_color(st), bg=bg, width=col_widths[-2],
                        anchor='center').pack(side=tk.LEFT, padx=1, pady=3)

                # 查看按钮
                tk.Button(row, text='查看', font=('SimHei', 8),
                         bg='#3498DB', fg='white', bd=0, width=4,
                         cursor='hand2',
                         command=lambda r=req: show_detail(r)).pack(side=tk.LEFT, padx=1, pady=3)

    # ========== 初始化 ==========
    show_default()
    refresh_table()
