# 疫苗类别管理相关页面

import tkinter as tk
from tkinter import ttk, messagebox


def _sync_categories_from_vaccines(service):
    """
    从疫苗数据中自动提取并同步类别信息
    解决：vaccines.json中有类别，但categories.json为空导致不显示的问题
    """
    # 收集所有疫苗中出现的类别名称（去重）
    vaccine_categories = set()
    for vaccine in service.vaccines:
        category = vaccine.get('category', '').strip()
        if category and category not in ['', '-', '无']:
            vaccine_categories.add(category)

    # 获取当前categories列表中的类别名称
    existing_names = {c.get('name', '') for c in (service.categories or []) if c.get('name')}

    # 添加新的类别
    new_count = 0
    for cat_name in vaccine_categories:
        if cat_name not in existing_names and cat_name not in ['', '-']:
            new_cat = {
                'id': service.get_next_category_id() if hasattr(service, 'get_next_category_id') else len(service.categories or []) + 1,
                'name': cat_name,
                'description': '从疫苗记录自动同步'
            }

            if not service.categories:
                service.categories = []

            service.categories.append(new_cat)
            existing_names.add(cat_name)
            new_count += 1

    # 如果有新增的类别，保存到文件
    if new_count > 0:
        try:
            service.repository.save_categories(service.categories)
        except Exception as e:
            print(f'保存类别数据失败: {e}')


def render_cat_define(parent, service):
    """类别定义页面 - 左右分栏布局（左侧表格 + 右侧编辑面板）"""

    title = tk.Label(parent, text='📂 类别定义',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=(15, 10))

    # 自动同步：从疫苗数据中提取类别到categories列表
    _sync_categories_from_vaccines(service)

    # 说明区域
    info_frame = tk.Frame(parent, bg='#E8F4F8', padx=15, pady=8)
    info_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

    tk.Label(info_frame,
            text='💡 管理疫苗分类。每个疫苗必须属于一个类别（如：灭活疫苗、减毒活疫苗等）。',
            font=('SimHei', 10), fg='#1E90FF', bg='#E8F4F8').pack(anchor=tk.W)

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

    headers = ['ID', '名称', '描述', '操作']
    header_widths = [8, 24, 36, 16]

    for h, w in zip(headers, header_widths):
        tk.Label(header_frame, text=h, font=('SimHei', 11, 'bold'),
                fg='white', bg='#2C3E50', width=w).pack(side=tk.LEFT, padx=1, pady=6)

    # 数据显示区域
    data_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
    data_frame.pack(fill=tk.X)

    # 底部计数
    count_label = tk.Label(left_panel, text='共 0 个类别', font=('SimHei', 10), fg='#666', bg='#FFFFFF')
    count_label.pack(anchor=tk.W, pady=(5, 0))

    # ==================== 右侧面板（编辑/新增表单）====================
    right_panel = tk.Frame(main_container, bg='#F8F9FA', relief=tk.GROOVE, bd=2)
    right_panel.grid(row=0, column=1, sticky='nsew')

    # 详情标题
    detail_header = tk.Frame(right_panel, bg='#2C3E50')
    detail_header.pack(fill=tk.X)

    detail_title_label = tk.Label(detail_header, text='📝 类别信息',
                                 font=('SimHei', 12, 'bold'), fg='white', bg='#2C3E50')
    detail_title_label.pack(pady=10)

    # 详情内容区
    detail_container = tk.Frame(right_panel, bg='#F8F9FA')
    detail_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    # 默认提示
    def show_default_hint():
        """恢复右侧面板默认提示"""
        for widget in detail_container.winfo_children():
            widget.destroy()
        detail_title_label.config(text='📝 类别信息')

        default_hint = tk.Label(detail_container,
                                text='💡 请点击左侧"编辑"按钮\n\n在此处编辑类别信息\n\n或点击下方"新增类别"按钮\n添加新类别',
                                font=('SimHei', 11), fg='#999', bg='#F8F9FA',
                                justify=tk.CENTER)
        default_hint.pack(expand=True)

    show_default_hint()

    def show_edit_form(category):
        """在右侧面板显示编辑表单"""
        # 清除旧内容
        for widget in detail_container.winfo_children():
            widget.destroy()

        detail_title_label.config(text=f'✏️ 编辑类别 - {category.get("name", "")}')

        form = tk.Frame(detail_container, bg='#FFFFFF', padx=10, pady=10)
        form.pack(fill=tk.BOTH, expand=True)

        name_var = tk.StringVar(value=str(category.get('name', '')))
        desc_var = tk.StringVar(value=str(category.get('description', '')))

        tk.Label(form, text='* 类别名称：', font=('SimHei', 10),
                bg='#FFFFFF').grid(row=0, column=0, sticky=tk.E, pady=5, padx=(0, 5))
        tk.Entry(form, textvariable=name_var, font=('SimHei', 11),
                width=26).grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(form, text='描述：', font=('SimHei', 10),
                bg='#FFFFFF').grid(row=1, column=0, sticky=tk.NE, pady=5, padx=(0, 5))
        desc_entry = tk.Text(form, font=('SimHei', 11), width=26, height=4)
        desc_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        desc_entry.insert('1.0', desc_var.get())

        def save_changes():
            name_val = name_var.get().strip()
            if not name_val:
                messagebox.showerror('错误', '请填写类别名称！')
                return

            # 纯数字检查
            if name_val.isdigit():
                messagebox.showerror('错误', f'类别名称不能为纯数字: "{name_val}"')
                return

            # 重复名称检查（排除自身）
            cat_id = category.get('id')
            for c in (service.categories or []):
                if c.get('name', '') == name_val and c.get('id') != cat_id:
                    messagebox.showerror('错误', f'类别名称 "{name_val}" 已存在（ID: {c.get("id")}），请使用其他名称')
                    return

            category['name'] = name_val
            category['description'] = desc_entry.get('1.0', 'end').strip()
            service.save_data()
            service.log_operation(f"修改类别：{name_val}")
            messagebox.showinfo('成功', f'类别 {name_val} 已更新')
            refresh_table()
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

        detail_title_label.config(text='➕ 新增疫苗类别')

        form = tk.Frame(detail_container, bg='#FFFFFF', padx=10, pady=10)
        form.pack(fill=tk.BOTH, expand=True)

        name_var = tk.StringVar()
        desc_var = tk.StringVar()

        tk.Label(form, text='* 类别名称：', font=('SimHei', 10),
                bg='#FFFFFF').grid(row=0, column=0, sticky=tk.E, pady=5, padx=(0, 5))
        tk.Entry(form, textvariable=name_var, font=('SimHei', 11),
                width=26).grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(form, text='描述：', font=('SimHei', 10),
                bg='#FFFFFF').grid(row=1, column=0, sticky=tk.NE, pady=5, padx=(0, 5))
        tk.Entry(form, textvariable=desc_var, font=('SimHei', 11),
                width=26).grid(row=1, column=1, sticky=tk.W, pady=5)

        def submit_new():
            name_val = name_var.get().strip()
            if not name_val:
                messagebox.showerror('错误', '请填写类别名称！')
                return

            # 纯数字检查
            if name_val.isdigit():
                messagebox.showerror('错误', f'类别名称不能为纯数字: "{name_val}"')
                return

            # 重复名称检查
            existing_names = {c.get('name', '') for c in (service.categories or []) if c.get('name')}
            if name_val in existing_names:
                messagebox.showerror('错误', f'类别名称 "{name_val}" 已存在，请使用其他名称')
                return

            new_cat = {
                'id': service.get_next_category_id(),
                'name': name_val,
                'description': desc_var.get().strip()
            }

            if not service.categories:
                service.categories = []
            service.categories.append(new_cat)
            service.save_data()
            service.log_operation(f"添加类别：{new_cat['name']}")

            messagebox.showinfo('成功', f'类别 {new_cat["name"]} 添加成功！')
            refresh_table()
            show_default_hint()

        btn_row = tk.Frame(detail_container, bg='#F8F9FA')
        btn_row.pack(fill=tk.X, pady=(15, 0))

        tk.Button(btn_row, text='✅ 提交', command=submit_new,
                 font=('SimHei', 11), bg='#00CC00', fg='white', bd=0, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_row, text='取消', command=show_default_hint,
                 font=('SimHei', 11), bg='#999', fg='white', bd=0, width=10).pack(side=tk.LEFT, padx=5)

    def delete_category(cat_id):
        """删除类别"""
        used_in_vaccines = [v for v in service.vaccines
                           if v.get('category') and str(v['id']) == str(cat_id)]

        if used_in_vaccines:
            messagebox.showwarning('警告',
                                 f'该类别下还有 {len(used_in_vaccines)} 条疫苗记录\n请先转移或删除这些记录后再删除该类别')
            return

        if messagebox.askyesno('确认删除', '确定要删除该类别吗？'):
            categories_list = service.categories or []
            service.categories = [c for c in categories_list if c.get('id') != cat_id]
            service.save_data()
            messagebox.showinfo('成功', '已删除该类别')
            refresh_table()
            show_default_hint()

    def refresh_table():
        """刷新表格数据"""
        for widget in data_frame.winfo_children():
            widget.destroy()

        categories_list = service.categories or []

        if not categories_list:
            empty_label = tk.Label(data_frame, text='暂无类别记录',
                                  font=('SimHei', 12), fg='#999', bg='#FFFFFF')
            empty_label.pack(pady=30)
        else:
            for idx, cat in enumerate(categories_list):
                bg_color = '#F9F9F9' if idx % 2 == 0 else '#FFFFFF'
                row = tk.Frame(data_frame, bg=bg_color)
                row.pack(fill=tk.X)

                values = [
                    str(cat.get('id', '-')),
                    str(cat.get('name', '-'))[:22],
                    str(cat.get('description', '-'))[:34]
                ]

                for val, w in zip(values, header_widths[:-1]):
                    tk.Label(row, text=val, font=('SimHei', 10),
                            fg='#333', bg=bg_color, width=w).pack(side=tk.LEFT, padx=1, pady=4)

                btn_frame = tk.Frame(row, bg=bg_color)
                btn_frame.pack(side=tk.LEFT, padx=1)

                tk.Button(btn_frame, text='编辑', font=('SimHei', 9),
                         bg='#1E90FF', fg='white', bd=0, width=6,
                         command=lambda c=cat: show_edit_form(c)).pack(side=tk.LEFT, padx=1)
                tk.Button(btn_frame, text='删除', font=('SimHei', 9),
                         bg='#FF6347', fg='white', bd=0, width=6,
                         command=lambda cid=cat.get('id'): delete_category(cid)).pack(side=tk.LEFT, padx=1)

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

        count_label.config(text=f'共 {len(categories_list)} 个类别')

    # 底部按钮栏
    action_bar = tk.Frame(left_panel, bg='#FFFFFF')
    action_bar.pack(fill=tk.X, pady=(8, 0))

    tk.Button(action_bar, text='➕ 新增类别', command=show_add_form,
             font=('SimHei', 11), bg='#00CC00', fg='white', bd=0, width=12).pack(side=tk.LEFT, padx=5)

    # 初始加载
    refresh_table()

    # 绑定滚动事件
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
