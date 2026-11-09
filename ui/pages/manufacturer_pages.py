# 主体档案管理相关页面

import tkinter as tk
from tkinter import ttk, messagebox


def render_entity_archive(parent, service):
    """
    主体档案页面 - 生产厂家管理
    左右分栏：左侧表格列表(60%) + 右侧编辑面板(40%)
    """
    title = tk.Label(parent, text='📁 主体档案',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=(15, 10))

    # ==================== 全局搜索框 ====================
    search_frame = tk.Frame(parent, bg='#F5F5F5', padx=10, pady=8)
    search_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

    search_var = tk.StringVar()
    tk.Label(search_frame, text='🔍 搜索：', font=('SimHei', 11),
            bg='#F5F5F5').pack(side=tk.LEFT)
    search_entry = tk.Entry(search_frame, textvariable=search_var,
                           font=('SimHei', 11), width=30)
    search_entry.pack(side=tk.LEFT, padx=(0, 10))
    tk.Button(search_frame, text='搜索', command=lambda: refresh_manufacturer_table(search_var.get().strip() or None),
             font=('SimHei', 10), bg='#1E90FF', fg='white', bd=0).pack(side=tk.LEFT)

    # ==================== 左右分栏主容器 ====================
    main_container = tk.Frame(parent, bg='#FFFFFF')
    main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

    # 配置网格布局权重
    main_container.columnconfigure(0, weight=6)   # 左侧60%
    main_container.columnconfigure(1, weight=4)   # 右侧40%
    main_container.rowconfigure(0, weight=1)

    # ==================== 左侧面板（表格列表）====================
    left_panel = tk.Frame(main_container, bg='#FFFFFF')
    left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))

    # 表格容器（带滚动条）
    table_container = tk.Frame(left_panel, bg='#E8E8E8', relief=tk.SUNKEN, bd=1)
    table_container.pack(fill=tk.BOTH, expand=True)

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

    headers = ['名称', '信用代码', '联系人', '电话', '操作']
    header_widths = [16, 18, 12, 14, 16]

    for h, w in zip(headers, header_widths):
        tk.Label(header_frame, text=h, font=('SimHei', 11, 'bold'),
                fg='white', bg='#2C3E50', width=w).pack(side=tk.LEFT, padx=1, pady=6)

    # 数据显示区域
    data_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
    data_frame.pack(fill=tk.X)

    # 底部计数
    count_label = tk.Label(left_panel, text='共 0 家厂家', font=('SimHei', 10), fg='#666', bg='#FFFFFF')
    count_label.pack(anchor=tk.W, pady=(5, 0))

    # ==================== 右侧面板（编辑/新增表单）====================
    right_panel = tk.Frame(main_container, bg='#F8F9FA', relief=tk.GROOVE, bd=2)
    right_panel.grid(row=0, column=1, sticky='nsew')

    # 详情标题
    detail_header = tk.Frame(right_panel, bg='#2C3E50')
    detail_header.pack(fill=tk.X)

    detail_title_label = tk.Label(detail_header, text='📝 厂家信息',
                                 font=('SimHei', 12, 'bold'), fg='white', bg='#2C3E50')
    detail_title_label.pack(pady=10)

    # 详情内容区（可滚动）
    detail_container = tk.Frame(right_panel, bg='#F8F9FA')
    detail_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    # 默认提示
    def show_default_hint():
        """恢复右侧面板默认提示"""
        for widget in detail_container.winfo_children():
            widget.destroy()
        detail_title_label.config(text='📝 厂家信息')

        default_hint = tk.Label(detail_container,
                                text='💡 请点击左侧"编辑"按钮\n\n在此处编辑厂家信息\n\n或点击下方"新增记录"按钮\n添加新厂家',
                                font=('SimHei', 11), fg='#999', bg='#F8F9FA',
                                justify=tk.CENTER)
        default_hint.pack(expand=True)

    show_default_hint()

    # 当前编辑模式: None=默认, 'edit'=编辑, 'add'=新增
    edit_mode = {'type': None, 'data': None}

    def show_edit_form(manufacturer):
        """在右侧面板显示编辑表单"""
        # 清除旧内容
        for widget in detail_container.winfo_children():
            widget.destroy()

        detail_title_label.config(text=f'✏️ 编辑厂家 - {manufacturer.get("name", "")}')
        edit_mode['type'] = 'edit'
        edit_mode['data'] = manufacturer

        form = tk.Frame(detail_container, bg='#FFFFFF', padx=10, pady=10)
        form.pack(fill=tk.BOTH, expand=True)

        # 编辑字段
        fields = {}
        field_configs = [
            ('name', '* 厂家名称'),
            ('credit_code', '信用代码'),
            ('contact', '联系人'),
            ('phone', '联系电话'),
            ('address', '地址'),
            ('remark', '备注')
        ]

        for i, (key, label) in enumerate(field_configs):
            tk.Label(form, text=f'{label}：', font=('SimHei', 10),
                    bg='#FFFFFF').grid(row=i, column=0, sticky=tk.E, pady=4, padx=(0, 5))
            var = tk.StringVar(value=str(manufacturer.get(key, '')))
            fields[key] = var
            tk.Entry(form, textvariable=var, font=('SimHei', 10),
                    width=24).grid(row=i, column=1, sticky=tk.W, pady=4)

        def save_changes():
            manufacturer['name'] = fields['name'].get().strip()
            if not manufacturer['name']:
                messagebox.showerror('错误', '请填写厂家名称！')
                return
            manufacturer['credit_code'] = fields['credit_code'].get().strip()
            manufacturer['contact'] = fields['contact'].get().strip()
            manufacturer['phone'] = fields['phone'].get().strip()
            manufacturer['address'] = fields['address'].get().strip()
            manufacturer['remark'] = fields['remark'].get().strip()

            service.save_data()
            service.log_operation(f"编辑厂家：{manufacturer['name']}")
            messagebox.showinfo('成功', f'厂家 {manufacturer["name"]} 信息已保存')
            refresh_manufacturer_table(search_var.get().strip() or None)
            show_default_hint()

        btn_row = tk.Frame(detail_container, bg='#F8F9FA')
        btn_row.pack(fill=tk.X, pady=(15, 0))

        tk.Button(btn_row, text='💾 保存', command=save_changes,
                 font=('SimHei', 11), bg='#00CC00', fg='white', bd=0, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_row, text='取消', command=show_default_hint,
                 font=('SimHei', 11), bg='#999', fg='white', bd=0, width=10).pack(side=tk.LEFT, padx=5)

    def show_add_form():
        """在右侧面板显示新增表单"""
        # 清除旧内容
        for widget in detail_container.winfo_children():
            widget.destroy()

        detail_title_label.config(text='➕ 新增生产厂家')
        edit_mode['type'] = 'add'
        edit_mode['data'] = None

        form = tk.Frame(detail_container, bg='#FFFFFF', padx=10, pady=10)
        form.pack(fill=tk.BOTH, expand=True)

        new_fields = {}
        configs = [
            ('name', '* 厂家名称'),
            ('credit_code', '信用代码'),
            ('contact', '联系人'),
            ('phone', '联系电话'),
            ('address', '地址'),
            ('remark', '备注')
        ]

        for i, (key, label) in enumerate(configs):
            tk.Label(form, text=f'{label}：', font=('SimHei', 10),
                    bg='#FFFFFF').grid(row=i, column=0, sticky=tk.E, pady=4, padx=(0, 5))
            var = tk.StringVar()
            new_fields[key] = var
            tk.Entry(form, textvariable=var, font=('SimHei', 10),
                    width=24).grid(row=i, column=1, sticky=tk.W, pady=4)

        def submit_new():
            name_val = new_fields['name'].get().strip()
            if not name_val:
                messagebox.showerror('错误', '请填写厂家名称！')
                return

            new_mf = {
                'id': service.get_next_manufacturer_id(),
                'name': name_val,
                'credit_code': new_fields['credit_code'].get().strip(),
                'contact': new_fields['contact'].get().strip(),
                'phone': new_fields['phone'].get().strip(),
                'address': new_fields['address'].get().strip(),
                'remark': new_fields['remark'].get().strip()
            }

            service.manufacturers.append(new_mf)
            service.save_data()
            service.log_operation(f"添加厂家：{new_mf['name']}")

            messagebox.showinfo('成功', f'厂家 {new_mf["name"]} 添加成功！')
            refresh_manufacturer_table(search_var.get().strip() or None)
            show_default_hint()

        btn_row = tk.Frame(detail_container, bg='#F8F9FA')
        btn_row.pack(fill=tk.X, pady=(15, 0))

        tk.Button(btn_row, text='✅ 提交', command=submit_new,
                 font=('SimHei', 11), bg='#00CC00', fg='white', bd=0, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_row, text='取消', command=show_default_hint,
                 font=('SimHei', 11), bg='#999', fg='white', bd=0, width=10).pack(side=tk.LEFT, padx=5)

    def delete_manufacturer(mf_id):
        """删除厂家"""
        if messagebox.askyesno('确认删除', '确定要删除该厂家吗？此操作不可恢复。'):
            service.manufacturers = [m for m in service.manufacturers if m.get('id') != mf_id]
            service.save_data()
            messagebox.showinfo('成功', '已删除该厂家记录')
            refresh_manufacturer_table(search_var.get().strip() or None)
            show_default_hint()

    def refresh_manufacturer_table(search_text=None):
        """刷新厂家表格数据"""
        # 清除旧数据
        for widget in data_frame.winfo_children():
            widget.destroy()

        manufacturers_list = service.manufacturers or []
        if search_text:
            manufacturers_list = [m for m in manufacturers_list
                                if search_text.lower() in str(m.get('name', '')).lower() or
                                   search_text in str(m.get('contact', ''))]

        if not manufacturers_list:
            empty_label = tk.Label(data_frame, text='暂无厂家记录',
                                  font=('SimHei', 12), fg='#999', bg='#FFFFFF')
            empty_label.pack(pady=30)
        else:
            for idx, mf in enumerate(manufacturers_list[:20]):
                bg_color = '#F9F9F9' if idx % 2 == 0 else '#FFFFFF'
                row = tk.Frame(data_frame, bg=bg_color)
                row.pack(fill=tk.X)

                values = [
                    str(mf.get('name', '-'))[:14],
                    str(mf.get('credit_code', '-'))[:16],
                    str(mf.get('contact', '-'))[:10],
                    str(mf.get('phone', '-'))[:12]
                ]

                for val, w in zip(values, header_widths[:-1]):
                    tk.Label(row, text=val, font=('SimHei', 10),
                            fg='#333', bg=bg_color, width=w).pack(side=tk.LEFT, padx=1, pady=4)

                # 操作按钮
                btn_frame = tk.Frame(row, bg=bg_color)
                btn_frame.pack(side=tk.LEFT, padx=1)

                tk.Button(btn_frame, text='编辑', font=('SimHei', 9),
                         bg='#1E90FF', fg='white', bd=0, width=5,
                         command=lambda m=mf: show_edit_form(m)).pack(side=tk.LEFT, padx=1)
                tk.Button(btn_frame, text='删除', font=('SimHei', 9),
                         bg='#FF6347', fg='white', bd=0, width=5,
                         command=lambda mid=mf.get('id'): delete_manufacturer(mid)).pack(side=tk.LEFT, padx=1)

                # 行悬停效果
                def on_enter(e, r=row):
                    r.config(bg='#E3F2FD')
                def on_leave(e, r=row, bg=bg_color):
                    r.config(bg=bg)

                row.bind('<Enter>', lambda e, r=row: on_enter(e, r))
                row.bind('<Leave>', lambda e, r=row, bg=bg_color: on_leave(e, r, bg))
                for child in row.winfo_children():
                    child.bind('<Enter>', lambda e, r=row: on_enter(e, r))
                    child.bind('<Leave>', lambda e, r=row, bg=bg_color: on_leave(e, r, bg))

        count_label.config(text=f'共 {len(manufacturers_list)} 家厂家')

    # 底部按钮栏
    action_bar = tk.Frame(left_panel, bg='#FFFFFF')
    action_bar.pack(fill=tk.X, pady=(8, 0))

    tk.Button(action_bar, text='➕ 新增记录', command=show_add_form,
             font=('SimHei', 11), bg='#00CC00', fg='white', bd=0, width=12).pack(side=tk.LEFT, padx=5)

    # 初始加载
    refresh_manufacturer_table()

    # 绑定滚动事件
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
