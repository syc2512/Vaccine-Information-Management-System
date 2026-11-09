# 系统管理相关页面

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # 全局导入ttk模块


def render_permission_mgmt(parent, service):
    # 权限管理

    title = tk.Label(parent, text='👥 权限管理',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)

    # 说明区域（标注降级提示）
    note_frame = tk.Frame(parent, bg='#FFF3E0', padx=15, pady=8)
    note_frame.pack(fill=tk.X, padx=40, pady=(0, 15))
    tk.Label(note_frame,
            text='💡 可维护用户账号与角色。密码采用 PBKDF2 哈希保存，编辑时留空表示不修改。',
            font=('SimHei', 10), fg='#FF9900', bg='#FFF3E0').pack(anchor=tk.W)

    # 表格容器
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

    headers = ['用户名', '角色', '状态']
    header_widths = [18, 16, 10]

    for h, w in zip(headers, header_widths):
        tk.Label(header_frame, text=h, font=('SimHei', 11, 'bold'),
                fg='white', bg='#2C3E50', width=w).pack(side=tk.LEFT, padx=1, pady=6)

    # 数据显示区域
    data_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
    data_frame.pack(fill=tk.X)

    def show_user_detail(user):
        """查看/编辑用户详情"""
        detail_win = tk.Toplevel(parent)
        detail_win.title('用户详情 / 编辑')
        detail_win.geometry('420x340')
        detail_win.grab_set()

        tk.Label(detail_win, text='用户信息', font=('SimHei', 14, 'bold'),
                fg='#333', bg='#FFFFFF').pack(pady=15)

        form = tk.Frame(detail_win, bg='#FFFFFF', padx=25, pady=10)
        form.pack(fill=tk.X)

        fields = {}
        configs = [
            ('username', '* 用户名'),
            ('password', '新密码（留空不修改）'),
            ('role', '角色'),
        ]

        for i, (key, label) in enumerate(configs):
            tk.Label(form, text=f'{label}：', font=('SimHei', 11),
                    bg='#FFFFFF').grid(row=i, column=0, sticky=tk.E, pady=4)
            var = tk.StringVar(value='' if key == 'password' else str(user.get(key, '')))
            fields[key] = var

            if key == 'role':
                roles_list = [r.get('name', '-') for r in (service.roles or [])] or ['管理员', '操作员']
                combo = ttk.Combobox(form, textvariable=var,
                                    values=roles_list,
                                    font=('SimHei', 11), width=22)
                combo.grid(row=i, column=1, sticky=tk.W, pady=4, padx=5)
            else:
                w = 24 if key != 'password' else 22
                entry = tk.Entry(form, textvariable=var, font=('SimHei', 11), width=w, show='*' if key == 'password' else '')
                entry.grid(row=i, column=1, sticky=tk.W, pady=4, padx=5)

        def save_changes():
            try:
                service.update_user(
                    user.get('id'),
                    fields['username'].get(),
                    fields['role'].get(),
                    fields['password'].get(),
                )
                messagebox.showinfo('成功', f'用户 {fields["username"].get()} 信息已更新')
                detail_win.destroy()
                refresh_table()
            except (ValueError, RuntimeError) as error:
                messagebox.showerror('保存失败', str(error))

        btn_row = tk.Frame(detail_win, bg='#FFFFFF')
        btn_row.pack(pady=20)

        tk.Button(btn_row, text='💾 保存', command=save_changes,
                 font=('SimHei', 11), bg='#00CC00', fg='white', bd=0, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_row, text='关闭', command=detail_win.destroy,
                 font=('SimHei', 11), bg='#999', fg='white', bd=0, width=10).pack(side=tk.LEFT, padx=5)

    def add_user():
        """新增用户弹窗"""
        add_win = tk.Toplevel(parent)
        add_win.title('新增用户')
        add_win.geometry('400x280')
        add_win.grab_set()

        tk.Label(add_win, text='➕ 新增系统用户', font=('SimHei', 14, 'bold'),
                fg='#1E90FF', bg='#FFFFFF').pack(pady=15)

        form = tk.Frame(add_win, bg='#FFFFFF', padx=25, pady=10)
        form.pack(fill=tk.X)

        new_fields = {}
        configs = [
            ('username', '* 用户名'),
            ('password', '* 密码'),
            ('role', '角色'),
        ]

        for i, (key, label) in enumerate(configs):
            tk.Label(form, text=f'{label}：', font=('SimHei', 11),
                    bg='#FFFFFF').grid(row=i, column=0, sticky=tk.E, pady=4)
            var = tk.StringVar()
            new_fields[key] = var

            if key == 'role':
                roles_list = [r.get('name', '-') for r in (service.roles or [])] or ['管理员', '操作员']
                ttk.Combobox(form, textvariable=var,
                            values=roles_list,
                            font=('SimHei', 11), width=20).grid(row=i, column=1, sticky=tk.W, pady=4, padx=5)
            else:
                w = 22 if key == 'username' else 20
                tk.Entry(form, textvariable=var, font=('SimHei', 11), width=w,
                        show='*' if key == 'password' else '').grid(row=i, column=1, sticky=tk.W, pady=4, padx=5)

        def submit_new():
            uname = new_fields['username'].get().strip()
            pwd_val = new_fields['password'].get().strip()

            if not uname:
                messagebox.showerror('错误', '请填写用户名！')
                return
            if not pwd_val:
                messagebox.showerror('错误', '请填写密码！')
                return

            try:
                service.create_user(
                    uname,
                    pwd_val,
                    new_fields['role'].get().strip() or '普通操作员',
                )
                messagebox.showinfo('成功', f'用户 {uname} 添加成功！')
                add_win.destroy()
                refresh_table()
            except (ValueError, RuntimeError) as error:
                messagebox.showerror('添加失败', str(error))

        btn_row = tk.Frame(add_win, bg='#FFFFFF')
        btn_row.pack(pady=20)

        tk.Button(btn_row, text='✅ 提交', command=submit_new,
                 font=('SimHei', 11), bg='#00CC00', fg='white', bd=0, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_row, text='取消', command=add_win.destroy,
                 font=('SimHei', 11), bg='#999', fg='white', bd=0, width=10).pack(side=tk.LEFT, padx=5)

    def delete_user(user_id):
        """删除用户"""
        if messagebox.askyesno('确认删除', '确定要删除该用户吗？'):
            try:
                service.delete_user(user_id)
                messagebox.showinfo('成功', '已删除该用户记录')
                refresh_table()
            except (ValueError, RuntimeError) as error:
                messagebox.showerror('删除失败', str(error))

    def refresh_table():
        """刷新用户表格数据"""
        for widget in data_frame.winfo_children():
            widget.destroy()

        users_list = service.users or []

        if not users_list:
            empty_label = tk.Label(data_frame, text='暂无用户记录',
                                  font=('SimHei', 12), fg='#999', bg='#FFFFFF')
            empty_label.pack(pady=30)
        else:
            for idx, user in enumerate(users_list):
                bg_color = '#F9F9F9' if idx % 2 == 0 else '#FFFFFF'
                row = tk.Frame(data_frame, bg=bg_color)
                row.pack(fill=tk.X)

                values = [
                    str(user.get('username', '-'))[:16],
                    str(user.get('role', '-'))[:14],
                    '启用' if user.get('status') == 'active' else '禁用'
                ]

                status_color = '#00CC00' if user.get('status') == 'active' else '#FF6347'

                for i, val in enumerate(values):
                    color = status_color if i == 2 else '#333'
                    w = header_widths[i]
                    tk.Label(row, text=val, font=('SimHei', 10),
                            fg=color, bg=bg_color, width=w).pack(side=tk.LEFT, padx=1, pady=4)

                # 操作按钮
                btn_frame = tk.Frame(row, bg=bg_color)
                btn_frame.pack(side=tk.LEFT, padx=1)

                tk.Button(btn_frame, text='编辑', font=('SimHei', 9),
                         bg='#1E90FF', fg='white', bd=0, width=5,
                         command=lambda u=user: show_user_detail(u)).pack(side=tk.LEFT, padx=1)
                tk.Button(btn_frame, text='删除', font=('SimHei', 9),
                         bg='#FF6347', fg='white', bd=0, width=5,
                         command=lambda uid=user.get('id'): delete_user(uid)).pack(side=tk.LEFT, padx=1)

    # 底部按钮栏
    action_bar = tk.Frame(parent, bg='#FFFFFF')
    action_bar.pack(fill=tk.X, padx=40, pady=(0, 20))

    tk.Button(action_bar, text='➕ 新增用户', command=add_user,
             font=('SimHei', 11), bg='#00CC00', fg='white', bd=0, width=12).pack(side=tk.LEFT, padx=5)
    tk.Label(action_bar,
            text=f'共 {len(service.users or [])} 个用户',
            font=('SimHei', 10), fg='#666', bg='#FFFFFF').pack(side=tk.RIGHT, padx=10)

    # 初始加载
    refresh_table()

    # 绑定滚动事件
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


def render_logs(parent, service):
    """操作日志页面（保持不变）"""
    title = tk.Label(parent, text='操作日志',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)

    if not service.operation_logs:
        tk.Label(parent, text='暂无操作日志',
                font=('SimHei', 14), bg='#FFFFFF').pack(pady=50)
        return

    # 显示最近的100条日志
    logs_to_show = service.operation_logs[-100:]

    list_frame = tk.Frame(parent, bg='#FFFFFF', padx=40)
    list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

    # 表头
    header = tk.Frame(list_frame, bg='#333')
    header.pack(fill=tk.X)
    tk.Label(header, text='时间', font=('SimHei', 11, 'bold'),
            fg='white', bg='#333', width=25).pack(side=tk.LEFT, padx=2)
    tk.Label(header, text='用户', font=('SimHei', 11, 'bold'),
            fg='white', bg='#333', width=10).pack(side=tk.LEFT, padx=2)
    tk.Label(header, text='操作内容', font=('SimHei', 11, 'bold'),
            fg='white', bg='#333', width=40).pack(side=tk.LEFT, padx=2)

    # 日志条目（倒序显示）
    for log in reversed(logs_to_show[:20]):
        row = tk.Frame(list_frame, bg='#FFFFFF')
        row.pack(fill=tk.X)

        tk.Label(row, text=log.get('time', '-'), font=('SimHei', 10),
                bg='#FFFFFF', width=25).pack(side=tk.LEFT, padx=2)
        tk.Label(row, text=log.get('user', '-'), font=('SimHei', 10),
                bg='#FFFFFF', width=10).pack(side=tk.LEFT, padx=2)
        tk.Label(row, text=log.get('action', '-')[:60], font=('SimHei', 10),
                bg='#FFFFFF', width=40).pack(side=tk.LEFT, padx=2)


def render_backup(parent, service):
    # 数据备份

    title = tk.Label(parent, text='💾 数据备份',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)

    # 备份说明
    mode_frame = tk.Frame(parent, bg='#FFF9E6', padx=15, pady=8)
    mode_frame.pack(fill=tk.X, padx=40, pady=(0, 15))
    tk.Label(mode_frame,
            text='✅ SQLite 在线备份：使用数据库一致性快照，不会复制正在写入的文件。',
            font=('SimHei', 11), fg='#FF9900', bg='#FFF9E6').pack(anchor=tk.W)

    # 备份操作区
    action_frame = tk.LabelFrame(parent, text='备份操作', font=('SimHei', 11),
                                bg='#F5F5F5', padx=20, pady=15)
    action_frame.pack(fill=tk.X, padx=40, pady=(0, 15))

    def do_backup():
        """创建真实的 SQLite 一致性备份"""
        backup_name = "正在创建数据库快照"
        progress_label = tk.Label(action_frame,
                                 text=f'📦 正在创建备份: {backup_name} ...\n请稍候...',
                                 font=('SimHei', 12), fg='#1E90FF', bg='#F5F5F5')
        progress_label.pack(pady=10)
        parent.update()

        try:
            backup_path = service.repository.create_backup()
            if not backup_path:
                messagebox.showerror('备份失败', '未能创建数据库备份，请检查数据目录权限。')
            else:
                messagebox.showinfo('备份成功', f'数据库备份已创建：\n{backup_path}')
                refresh_backup_list()
        finally:
            progress_label.destroy()

    tk.Button(action_frame, text='💾 立即创建备份', command=do_backup,
             font=('SimHei', 13), bg='#00CC00', fg='white', bd=0, width=18).pack(pady=10)

    # 备份列表区域
    list_frame = tk.LabelFrame(parent, text='备份历史记录', font=('SimHei', 11),
                              bg='#FFFFFF', padx=15, pady=10)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 15))

    def delete_from_list(item_id):
        """删除真实备份文件"""
        if messagebox.askyesno('确认删除', '确定要删除该备份文件吗？'):
            if service.repository.delete_backup(item_id):
                messagebox.showinfo('删除成功', '备份文件已删除。')
                refresh_backup_list()
            else:
                messagebox.showerror('删除失败', '备份文件不存在或无法删除。')

    def restore_backup(backup_name):
        """从 SQLite 快照恢复数据"""
        if messagebox.askyesno('确认恢复',
                              f'确定要从备份恢复吗？\n\n'
                              f'备份: {backup_name}\n\n'
                              '⚠️ 此操作会覆盖当前数据库中的全部业务数据。'):
            if service.repository.restore_from_backup(backup_name):
                service.reload_data()
                messagebox.showinfo('恢复成功', f'数据库已从 {backup_name} 恢复。')
            else:
                messagebox.showerror('恢复失败', '备份文件无效或恢复过程中发生错误。')

    def refresh_backup_list():
        """刷新真实备份列表"""
        nonlocal list_data_frame
        try:
            list_data_frame.destroy()
        except Exception:
            pass

        list_data_frame = tk.Frame(list_frame, bg='#FFFFFF')
        list_data_frame.pack(fill=tk.X, pady=5)

        backups = [
            (
                item['filename'],
                item['modified'],
                f"{max(1, round(item['size'] / 1024))} KB",
            )
            for item in service.repository.list_backups()
        ]

        if not backups:
            tk.Label(list_data_frame, text='暂无备份记录',
                    font=('SimHei', 12), fg='#999', bg='#FFFFFF').pack(pady=30)
        else:
            # 表头
            header = tk.Frame(list_data_frame, bg='#E8E8E8')
            header.pack(fill=tk.X, pady=(0, 5))
            for col in ['文件名', '创建时间', '大小', '操作']:
                tk.Label(header, text=col, font=('SimHei', 10, 'bold'),
                        fg='#333', bg='#E8E8E8', width=18).pack(side=tk.LEFT, padx=3, pady=4)

            # 数据行
            for i, (name, date_time, size) in enumerate(backups):
                bg_color = '#F9F9F9' if i % 2 == 0 else '#FFFFFF'
                row = tk.Frame(list_data_frame, bg=bg_color)
                row.pack(fill=tk.X)

                tk.Label(row, text=name, font=('SimHei', 10),
                        fg='#333', bg=bg_color, width=22).pack(side=tk.LEFT, padx=3, pady=3)
                tk.Label(row, text=date_time, font=('SimHei', 10),
                        fg='#666', bg=bg_color, width=16).pack(side=tk.LEFT, padx=3, pady=3)
                tk.Label(row, text=size, font=('SimHei', 10),
                        fg='#666', bg=bg_color, width=10).pack(side=tk.LEFT, padx=3, pady=3)

                btn_row = tk.Frame(row, bg=bg_color)
                btn_row.pack(side=tk.LEFT)

                tk.Button(btn_row, text='恢复', font=('SimHei', 9),
                         bg='#1E90FF', fg='white', bd=0, width=5,
                         command=lambda n=name: restore_backup(n)).pack(side=tk.LEFT, padx=1)
                tk.Button(btn_row, text='删除', font=('SimHei', 9),
                         bg='#FF6347', fg='white', bd=0, width=5,
                         command=lambda n=name: delete_from_list(n)).pack(side=tk.LEFT, padx=1)

    list_data_frame = None

    # 初始加载备份列表
    refresh_backup_list()


def render_export(parent, service):
    # 数据导出

    title = tk.Label(parent, text='📤 数据导出',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)

    # 说明区域
    note_frame = tk.Frame(parent, bg='#E8F4E8', padx=15, pady=8)
    note_frame.pack(fill=tk.X, padx=40, pady=(0, 15))
    tk.Label(note_frame,
            text='💡 支持导出为CSV格式（Excel可打开）。XLSX格式需要安装openpyxl库。',
            font=('SimHei', 10), fg='#00AA00', bg='#E8F4E8').pack(anchor=tk.W)

    # 配置区域
    config_frame = tk.LabelFrame(parent, text='导出配置', font=('SimHei', 11),
                                bg='#F5F5F5', padx=15, pady=10)
    config_frame.pack(fill=tk.X, padx=40, pady=(0, 15))

    # 第一行：导出类型 + 格式
    row1 = tk.Frame(config_frame, bg='#F5F5F5')
    row1.pack(fill=tk.X, pady=5)

    tk.Label(row1, text='* 导出类型：', font=('SimHei', 11),
            bg='#F5F5F5').pack(side=tk.LEFT)
    export_type_var = tk.StringVar(value='疫苗清单')

    type_combo = ttk.Combobox(row1, textvariable=export_type_var,
                             values=['疫苗清单', '入库记录', '厂家列表', '供应商列表', '操作日志'],
                             state='readonly', width=16, font=('SimHei', 11))
    type_combo.pack(side=tk.LEFT, padx=(0, 20))

    tk.Label(row1, text='* 格式：', font=('SimHei', 11),
            bg='#F5F5F5').pack(side=tk.LEFT)
    format_var = tk.StringVar(value='CSV')
    format_combo = ttk.Combobox(row1, textvariable=format_var,
                              values=['CSV'],
                              state='readonly', width=8, font=('SimHei', 11))
    format_combo.pack(side=tk.LEFT)

    # 第二行：动态筛选项
    row2 = tk.Frame(config_frame, bg='#F5F5F5')
    row2.pack(fill=tk.X, pady=5)

    filter_label = tk.Label(row2, text='筛选条件：', font=('SimHei', 11),
                           bg='#F5F5F5')
    filter_label.pack(side=tk.LEFT)

    # 根据导出类型显示不同筛选条件
    dynamic_filter_var = tk.StringVar()
    def update_dynamic_filter(*args):
        for widget in row2.winfo_children()[1:]:  # 保留第一个label
            widget.destroy()

        export_t = export_type_var.get()
        if export_t == '疫苗清单':
            categories = list(set(v.get('category', '') for v in (service.vaccines or []) if v.get('category')))
            ttk.Combobox(row2, textvariable=dynamic_filter_var,
                        values=['全部'] + categories,
                        state='readonly', width=16, font=('SimHei', 11)).pack(side=tk.LEFT, padx=(5, 10))
        elif export_t == '入库记录':
            tk.Entry(row2, textvariable=dynamic_filter_var,
                    font=('SimHei', 11), width=18).pack(side=tk.LEFT, padx=(5, 10))
        else:
            dynamic_filter_var.set('')
        tk.Button(row2, text='预览数量', command=lambda: preview_count(),
                 font=('SimHei', 10), bg='#1E90FF', fg='white', bd=0).pack(side=tk.LEFT)

    type_combo.bind('<<ComboboxSelected>>', update_dynamic_filter)

    # 初始化动态筛选
    update_dynamic_filter()

    # 预览结果显示
    preview_label = tk.Label(config_frame, text='', font=('SimHei', 10), fg='#666', bg='#F5F5F5')
    preview_label.pack(anchor=tk.W, pady=(8, 0))

    def preview_count():
        """预览待导出的记录数"""
        export_t = export_type_var.get()
        count_map = {
            '疫苗清单': len(service.vaccines or []),
            '入库记录': len([v for v in (service.vaccines or []) if v.get('入库单号')]),
            '厂家列表': len(service.manufacturers or []),
            '供应商列表': len(service.suppliers or []),
            '操作日志': len(service.operation_logs or [])
        }
        count = count_map.get(export_t, 0)
        preview_label.config(text=f'✅ 预计导出 {count} 条记录')

    preview_count()  # 初始显示

    # 操作按钮区
    btn_frame = tk.Frame(parent, bg='#FFFFFF')
    btn_frame.pack(pady=20)

    def do_export():
        """执行导出操作（CSV格式）"""
        import csv
        from datetime import datetime as dt

        format_val = format_var.get()
        if format_val != 'CSV':
            messagebox.showwarning('功能开发中',
                                  f'{format_val} 格式导出功能开发中\n'
                                  f'如需使用请安装 openpyxl 库：pip install openpyxl')
            return

        export_t = export_type_var.get()
        data_to_export = []
        fieldnames = []

        # 准备数据
        if export_t == '疫苗清单':
            fieldnames = ['ID', '名称', '类别', '生产厂家', '批次号', '数量', '生产日期', '有效期至', '状态']
            for v in (service.vaccines or []):
                data_to_export.append({
                    'ID': str(v.get('id', '')),
                    '名称': v.get('name', ''),
                    '类别': v.get('category', ''),
                    '生产厂家': v.get('manufacturer', ''),
                    '批次号': v.get('batch_number', ''),
                    '数量': str(v.get('quantity', '')),
                    '生产日期': v.get('production_date', ''),
                    '有效期至': v.get('expiry_date', ''),
                    '状态': v.get('status', '')
                })

        elif export_t == '入库记录':
            fieldnames = ['单据号', '疫苗名称', '批号', '数量', '日期']
            for v in (service.vaccines or []):
                if v.get('入库单号'):
                    data_to_export.append({
                        '单据号': v.get('入库单号', ''),
                        '疫苗名称': v.get('name', ''),
                        '批号': v.get('batch_number', ''),
                        '数量': str(v.get('quantity', '')),
                        '日期': v.get('入库时间', '')
                    })

        elif export_t == '厂家列表':
            fieldnames = ['ID', '名称', '信用代码', '联系人', '电话', '地址']
            for m in (service.manufacturers or []):
                data_to_export.append({
                    'ID': str(m.get('id', '')),
                    '名称': m.get('name', ''),
                    '信用代码': m.get('credit_code', ''),
                    '联系人': m.get('contact', ''),
                    '电话': m.get('phone', ''),
                    '地址': m.get('address', '')
                })

        elif export_t == '供应商列表':
            fieldnames = ['ID', '名称', '联系人', '电话', '地址', '邮箱']
            for s in (service.suppliers or []):
                data_to_export.append({
                    'ID': str(s.get('id', '')),
                    '名称': s.get('name', ''),
                    '联系人': s.get('contact', ''),
                    '电话': s.get('phone', ''),
                    '地址': s.get('address', ''),
                    '邮箱': s.get('email', '')
                })

        elif export_t == '操作日志':
            fieldnames = ['时间', '用户', '操作内容']
            for log in reversed((service.operation_logs or [])[-100:]):
                data_to_export.append({
                    '时间': log.get('time', ''),
                    '用户': log.get('user', ''),
                    '操作内容': log.get('action', '')
                })

        if not data_to_export:
            messagebox.showwarning('提示', f'{export_t} 无数据可导出')
            return

        # 选择保存位置
        filename = f"{export_t}_{dt.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv")],
            initialfilename=filename
        )

        if not filepath:
            return  # 用户取消

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_to_export)

            messagebox.showinfo('✅ 导出成功',
                              f'文件已保存至:\n{filepath}\n\n'
                              f'共 {len(data_to_export)} 条记录\n'
                              f'格式: CSV (UTF-8编码，Excel可直接打开)')

            service.log_operation(f"导出{export_t}数据")

        except Exception as e:
            messagebox.showerror('❌ 导出失败', f'导出过程中发生错误:\n{str(e)}')

    tk.Button(btn_frame, text='📥 开始导出', command=do_export,
             font=('SimHei', 13), bg='#FF9900', fg='white', bd=0, width=15).pack(side=tk.LEFT, padx=5)


def render_settings(parent, service):
    """系统设置页面 - 使用 Notebook 多标签页分类展示"""
    title = tk.Label(parent, text='⚙️ 系统设置',
                    font=('SimHei', 18, 'bold'), fg='#333', bg='#FFFFFF')
    title.pack(pady=20)

    # 获取当前设置
    settings = service.settings

    # 创建 Notebook 标签控件
    notebook = ttk.Notebook(parent)
    notebook.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 15))

    # ==================== Tab1: 基本设置 ====================
    tab_basic = tk.Frame(notebook, bg='#FFFFFF')
    notebook.add(tab_basic, text='  基本设置  ')

    basic_inner = tk.Frame(tab_basic, bg='#FFFFFF', padx=30, pady=20)
    basic_inner.pack(fill=tk.X, anchor=tk.N)

    tk.Label(basic_inner, text='系统名称：', font=('SimHei', 12),
            bg='#FFFFFF').grid(row=0, column=0, sticky=tk.W, pady=8)
    system_name_var = tk.StringVar(value=settings.get('system_name', '疫苗管理系统'))
    tk.Entry(basic_inner, textvariable=system_name_var,
            font=('SimHei', 12), width=30, relief=tk.SOLID, bd=1).grid(row=0, column=1, pady=8, padx=(10, 0))

    tk.Label(basic_inner, text='最低库存预警值：', font=('SimHei', 12),
            bg='#FFFFFF').grid(row=1, column=0, sticky=tk.W, pady=8)
    min_stock_var = tk.StringVar(value=str(settings.get('min_stock', 10)))
    tk.Spinbox(basic_inner, textvariable=min_stock_var, from_=0, to=999999,
              font=('SimHei', 12), width=10, relief=tk.SOLID, bd=1).grid(row=1, column=1, pady=8, padx=(10, 0), sticky=tk.W)
    tk.Label(basic_inner, text='（库存低于此值时触发预警）', font=('SimHei', 10),
            fg='#999', bg='#FFFFFF').grid(row=1, column=2, sticky=tk.W, padx=(5, 0))

    # ==================== Tab2: 预警通知设置 ====================
    tab_alert = tk.Frame(notebook, bg='#FFFFFF')
    notebook.add(tab_alert, text='  预警通知  ')

    alert_inner = tk.Frame(tab_alert, bg='#FFFFFF', padx=30, pady=20)
    alert_inner.pack(fill=tk.X, anchor=tk.N)

    tk.Label(alert_inner, text='有效期预警天数：', font=('SimHei', 12),
            bg='#FFFFFF').grid(row=0, column=0, sticky=tk.W, pady=8)
    expiry_warning_var = tk.StringVar(value=str(settings.get('expiry_warning_days', 30)))
    tk.Spinbox(alert_inner, textvariable=expiry_warning_var, from_=1, to=365,
              font=('SimHei', 12), width=10, relief=tk.SOLID, bd=1).grid(row=0, column=1, pady=8, padx=(10, 0), sticky=tk.W)
    tk.Label(alert_inner, text='（距有效期截止日少于此天数时预警）', font=('SimHei', 10),
            fg='#999', bg='#FFFFFF').grid(row=0, column=2, sticky=tk.W, padx=(5, 0))

    enable_popup_var = tk.BooleanVar(value=settings.get('enable_popup_alert', True))
    tk.Checkbutton(alert_inner, text='启用弹窗提醒', variable=enable_popup_var,
                  font=('SimHei', 12), bg='#FFFFFF',
                  activebackground='#FFFFFF',
                  onvalue=True, offvalue=False).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=12)
    tk.Label(alert_inner, text='（开启后，疫苗临期/库存不足时自动弹出预警窗口）', font=('SimHei', 10),
            fg='#999', bg='#FFFFFF').grid(row=1, column=2, sticky=tk.W, padx=(5, 0))

    # ==================== Tab3: 数据显示设置 ====================
    tab_display = tk.Frame(notebook, bg='#FFFFFF')
    notebook.add(tab_display, text='  数据显示  ')

    display_inner = tk.Frame(tab_display, bg='#FFFFFF', padx=30, pady=20)
    display_inner.pack(fill=tk.X, anchor=tk.N)

    tk.Label(display_inner, text='日期显示格式：', font=('SimHei', 12),
            bg='#FFFFFF').grid(row=0, column=0, sticky=tk.W, pady=8)
    date_format_var = tk.StringVar(value=settings.get('date_format', 'YYYY-MM-DD'))
    date_format_combo = ttk.Combobox(display_inner, textvariable=date_format_var,
                                    values=['YYYY-MM-DD', 'DD/MM/YYYY'],
                                    state='readonly', width=16, font=('SimHei', 12))
    date_format_combo.grid(row=0, column=1, pady=8, padx=(10, 0), sticky=tk.W)
    tk.Label(display_inner, text='（影响系统中所有日期的显示方式）', font=('SimHei', 10),
            fg='#999', bg='#FFFFFF').grid(row=0, column=2, sticky=tk.W, padx=(5, 0))

    # ==================== Tab4: 数据管理设置 ====================
    tab_data = tk.Frame(notebook, bg='#FFFFFF')
    notebook.add(tab_data, text='  数据管理  ')

    data_inner = tk.Frame(tab_data, bg='#FFFFFF', padx=30, pady=20)
    data_inner.pack(fill=tk.X, anchor=tk.N)

    # 自动备份开关（简化版，仅保留开关）
    enable_bak_var = tk.BooleanVar(value=settings.get('enable_auto_bak', True))
    tk.Checkbutton(data_inner, text='启用自动备份', variable=enable_bak_var,
                  font=('SimHei', 12), bg='#FFFFFF',
                  activebackground='#FFFFFF',
                  onvalue=True, offvalue=False).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=8)

    # 操作日志保留条数
    tk.Label(data_inner, text='操作日志保留条数：', font=('SimHei', 12),
            bg='#FFFFFF').grid(row=2, column=0, sticky=tk.W, pady=8)
    max_log_var = tk.StringVar(value=str(settings.get('max_log_entries', 1000)))
    tk.Spinbox(data_inner, textvariable=max_log_var, from_=100, to=100000, increment=100,
              font=('SimHei', 12), width=10, relief=tk.SOLID, bd=1).grid(row=2, column=1, pady=8, padx=(10, 0), sticky=tk.W)
    tk.Label(data_inner, text='（超过此数量的旧日志将被自动删除）', font=('SimHei', 10),
            fg='#999', bg='#FFFFFF').grid(row=2, column=2, sticky=tk.W, padx=(5, 0))

    # 自动清理过期数据
    auto_clean_var = tk.BooleanVar(value=settings.get('auto_clean_expired', False))
    tk.Checkbutton(data_inner, text='启用自动清理过期数据', variable=auto_clean_var,
                  font=('SimHei', 12), bg='#FFFFFF',
                  activebackground='#FFFFFF',
                  onvalue=True, offvalue=False).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=12)
    tk.Label(data_inner, text='（开启后，系统将定期清理已过期的疫苗数据）', font=('SimHei', 10),
            fg='#999', bg='#FFFFFF').grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=(20, 0))

    # ==================== Tab5: 疫苗业务规则设置 ====================
    tab_biz = tk.Frame(notebook, bg='#FFFFFF')
    notebook.add(tab_biz, text='  业务规则  ')

    biz_inner = tk.Frame(tab_biz, bg='#FFFFFF', padx=30, pady=20)
    biz_inner.pack(fill=tk.X, anchor=tk.N)

    force_audit_var = tk.BooleanVar(value=settings.get('force_outbound_audit', False))
    tk.Checkbutton(biz_inner, text='启用出库审核强制开关', variable=force_audit_var,
                  font=('SimHei', 12), bg='#FFFFFF',
                  activebackground='#FFFFFF',
                  onvalue=True, offvalue=False).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=8)
    tk.Label(biz_inner, text='（开启后，所有出库操作必须经过审核流程才能完成）', font=('SimHei', 10),
            fg='#999', bg='#FFFFFF').grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=(20, 0))

    # ==================== 底部保存按钮 ====================
    btn_frame = tk.Frame(parent, bg='#FFFFFF')
    btn_frame.pack(pady=15)

    def save_settings():
        """保存所有设置项到 settings 字典并持久化"""
        try:
            # 基本设置
            settings['system_name'] = system_name_var.get().strip()
            min_stock_val = int(min_stock_var.get())
            if min_stock_val < 0:
                raise ValueError('最低库存预警值不能为负数')
            settings['min_stock'] = min_stock_val

            # 预警通知设置
            expiry_val = int(expiry_warning_var.get())
            if expiry_val < 1 or expiry_val > 365:
                raise ValueError('有效期预警天数必须在 1~365 之间')
            settings['expiry_warning_days'] = expiry_val
            settings['enable_popup_alert'] = enable_popup_var.get()

            # 数据显示设置
            settings['date_format'] = date_format_var.get()

            # 数据管理设置
            settings['enable_auto_bak'] = enable_bak_var.get()
            log_entries = int(max_log_var.get())
            if log_entries < 100 or log_entries > 100000:
                raise ValueError('操作日志保留条数必须在 100~100000 之间')
            settings['max_log_entries'] = log_entries
            settings['auto_clean_expired'] = auto_clean_var.get()

            # 疫苗业务规则设置
            settings['force_outbound_audit'] = force_audit_var.get()

            # 持久化保存
            service.settings = settings
            service.repository.save_settings(settings)
            service.log_operation('更新系统设置')

            messagebox.showinfo('✅ 保存成功', '系统设置已更新并保存！')

        except ValueError as e:
            messagebox.showerror('❌ 输入错误', f'参数校验失败：{e}')
        except Exception as e:
            messagebox.showerror('❌ 保存失败', f'保存设置时发生错误：{e}')

    def reset_defaults():
        """恢复默认设置"""
        if not messagebox.askyesno('⚠️ 确认重置',
                                  '确定要恢复所有设置为默认值吗？\n\n'
                                  '此操作将覆盖当前所有设置，不可撤销！'):
            return

        from config.settings import DEFAULT_SETTINGS
        # 恢复 UI 控件值
        system_name_var.set(DEFAULT_SETTINGS['system_name'])
        min_stock_var.set(str(DEFAULT_SETTINGS['min_stock']))
        expiry_warning_var.set(str(DEFAULT_SETTINGS['expiry_warning_days']))
        enable_popup_var.set(DEFAULT_SETTINGS['enable_popup_alert'])
        date_format_var.set(DEFAULT_SETTINGS['date_format'])
        enable_bak_var.set(DEFAULT_SETTINGS.get('enable_auto_bak', True))
        max_log_var.set(str(DEFAULT_SETTINGS['max_log_entries']))
        auto_clean_var.set(DEFAULT_SETTINGS['auto_clean_expired'])
        force_audit_var.set(DEFAULT_SETTINGS['force_outbound_audit'])

        messagebox.showinfo('✅ 已重置', '所有设置项已恢复为默认值（尚未保存，请点击"保存设置"生效）')

    def cancel_changes():
        """放弃修改，恢复为当前已保存的设置值"""
        current = service.settings
        system_name_var.set(current.get('system_name', '疫苗管理系统'))
        min_stock_var.set(str(current.get('min_stock', 10)))
        expiry_warning_var.set(str(current.get('expiry_warning_days', 30)))
        enable_popup_var.set(current.get('enable_popup_alert', True))
        date_format_var.set(current.get('date_format', 'YYYY-MM-DD'))
        enable_bak_var.set(current.get('enable_auto_bak', True))
        max_log_var.set(str(current.get('max_log_entries', 1000)))
        auto_clean_var.set(current.get('auto_clean_expired', False))
        force_audit_var.set(current.get('force_outbound_audit', False))

    tk.Button(btn_frame, text='💾 保存设置', command=save_settings,
             font=('SimHei', 13), bg='#00CC00', fg='white', bd=0, width=15).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text='🔄 恢复默认', command=reset_defaults,
             font=('SimHei', 13), bg='#FF9900', fg='white', bd=0, width=15).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text='❌ 取消', command=cancel_changes,
             font=('SimHei', 13), bg='#999', fg='white', bd=0, width=12).pack(side=tk.LEFT, padx=10)
