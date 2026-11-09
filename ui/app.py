import datetime
import tkinter as tk
from tkinter import messagebox

from config.styles import MENU_BUTTON_STYLE, EXIT_BUTTON_STYLE, COLORS
from services.vaccine_service import vaccine_service


class VaccineManagementApp:
    
    def __init__(self, current_user=None, on_logout=None):
        self.root = None
        self.current_content = None
        self.current_page_var = None
        self.current_time_var = None
        
        self.pages = {}
        self.service = vaccine_service
        self.current_user = current_user or {
            'id': None,
            'username': '未登录',
            'role': '',
            'permissions': [],
        }
        self.service.set_current_user(self.current_user)
        self.on_logout = on_logout
    
    def run_main(self):
        print('Creating main window...')
        
        self.root = tk.Tk()
        self.root.title('疫苗信息管理系统')
        self.root.geometry('1200x700')
        self.root.resizable(True, True)
        
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.update()
        
        self.root.configure(bg=COLORS['primary_bg'])
        
        header_frame = tk.Frame(self.root, bg=COLORS['header_bg'], height=80)
        header_frame.pack(fill=tk.X)
        title = tk.Label(header_frame, text='💉 疫苗信息管理系统', 
                        font=('SimHei', 24, 'bold'), fg='white', bg=COLORS['header_bg'])
        title.pack(pady=20)
        
        # ====== 导航栏 ======
        nav_frame = tk.Frame(self.root, bg=COLORS['nav_bg'], height=35)
        nav_frame.pack(fill=tk.X)
        
        # 当前页面
        self.current_page_var = tk.StringVar(value='首页')
        nav_label = tk.Label(nav_frame, textvariable=self.current_page_var, 
                           font=('SimHei', 12), fg='#FF9900', bg=COLORS['nav_bg'])
        nav_label.pack(side=tk.LEFT, padx=20, pady=8)
        
        # 分隔
        sep_label = tk.Label(nav_frame, text='|', font=('SimHei', 12), 
                            fg='#666666', bg=COLORS['nav_bg'])
        sep_label.pack(side=tk.LEFT, padx=10)
        
        # 主页按钮
        home_btn = tk.Button(nav_frame, text='🏠 首页', font=('SimHei', 11), 
                            bg=COLORS['nav_bg'], fg='white', bd=0, cursor='hand2',
                            command=lambda: self.current_page_var.set('首页'))
        home_btn.pack(side=tk.LEFT, padx=5)
        
        # 时间
        self.current_time_var = tk.StringVar()
        time_label = tk.Label(nav_frame, textvariable=self.current_time_var, 
                             font=('SimHei', 11), fg='#CCCCCC', bg=COLORS['nav_bg'])
        time_label.pack(side=tk.RIGHT, padx=20)
        
        # 更新时间
        def update_time():
            now = datetime.datetime.now()
            self.current_time_var.set(now.strftime('%Y-%m-%d %H:%M:%S'))
            self.root.after(1000, update_time)
        update_time()
        
        # ====== 主内容 ======
        main_content = tk.Frame(self.root, bg=COLORS['primary_bg'])
        main_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        main_content.columnconfigure(0, weight=0)
        main_content.columnconfigure(1, weight=1)
        main_content.rowconfigure(0, weight=1)
        
        # ====== 左侧菜单 ======
        left_menu = tk.Frame(main_content, bg='#E8E8E8', width=200)
        left_menu.grid(row=0, column=0, sticky=tk.NS)
        left_menu.pack_propagate(False)
        
        scrollbar = tk.Scrollbar(left_menu, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        menu_canvas = tk.Canvas(left_menu, bg='#E8E8E8', width=185, yscrollcommand=scrollbar.set)
        menu_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=menu_canvas.yview)
        
        # 菜单内容
        menu_frame = tk.Frame(menu_canvas, bg='#E8E8E8')
        menu_canvas.create_window((0, 0), window=menu_frame, anchor=tk.NW)
        
        def update_scrollregion(event):
            menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
        menu_frame.bind("<Configure>", update_scrollregion)
        
        # 构建菜单
        self._build_left_menu(menu_frame, MENU_BUTTON_STYLE, EXIT_BUTTON_STYLE)
        
        # ====== 右侧内容 ======
        content_frame = tk.Frame(main_content, bg=COLORS['content_bg'])
        content_frame.grid(row=0, column=1, sticky=tk.NSEW)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # 当前内容
        self.current_content = tk.Frame(content_frame, bg=COLORS['content_bg'])
        self.current_content.grid(row=0, column=0, sticky=tk.NSEW)
        
        self.show_content('single_inventory')
        
        # 跑起主循环
        self.root.mainloop()
    
    def _build_left_menu(self, menu_frame, menu_button_style, exit_button_style):
        perms = self.current_user.get('permissions', [])

        # 左侧菜单标题
        menu_title = tk.Label(menu_frame, text='📋 功能菜单',
                            font=('SimHei', 14, 'bold'),
                            bg='#E8E8E8', fg='#333333')
        menu_title.pack(pady=15)

        # 显示当前登录用户
        user_label = tk.Label(menu_frame, 
                            text=f'👤 {self.current_user.get("username", "")} ({self.current_user.get("role", "")})',
                            font=('SimHei', 9),
                            bg='#E8E8E8', fg='#FF6600')
        user_label.pack(pady=(0, 5))

        tk.Frame(menu_frame, height=2, bg='#CCCCCC').pack(fill=tk.X)

        # ====== 基础数据管理 ======
        if 'basic_data' in perms:
            basic_menu = tk.Label(menu_frame, text='基础数据管理',
                                font=('SimHei', 12, 'bold'),
                                bg='#E8E8E8', fg='#1E90FF')
            basic_menu.pack(pady=(15, 5), anchor=tk.W, padx=10)

            # 疫苗入库
            warehouse_menu = tk.Label(menu_frame, text='疫苗入库',
                                    font=('SimHei', 11),
                                    bg='#E8E8E8', fg='#555555')
            warehouse_menu.pack(anchor=tk.W, padx=20)

            tk.Button(menu_frame, text='单个入库',
                     command=lambda: [self.set_page('基础数据管理 -> 疫苗入库 -> 单个入库'), self.show_content('single_inventory')],
                     **menu_button_style).pack(pady=2, padx=30, anchor=tk.W)
            tk.Button(menu_frame, text='批量入库',
                     command=lambda: [self.set_page('基础数据管理 -> 疫苗入库 -> 批量入库'), self.show_content('batch_inventory')],
                     **menu_button_style).pack(pady=2, padx=30, anchor=tk.W)
            tk.Button(menu_frame, text='入库审核',
                     command=lambda: [self.set_page('基础数据管理 -> 疫苗入库 -> 入库审核'), self.show_content('inventory_audit')],
                     **menu_button_style).pack(pady=2, padx=30, anchor=tk.W)
            tk.Button(menu_frame, text='入库单据',
                     command=lambda: [self.set_page('基础数据管理 -> 疫苗入库 -> 入库单据'), self.show_content('inventory_doc')],
                     **menu_button_style).pack(pady=2, padx=30, anchor=tk.W)
            tk.Button(menu_frame, text='入库记录',
                     command=lambda: [self.set_page('基础数据管理 -> 疫苗入库 -> 入库记录'), self.show_content('inventory_record')],
                     **menu_button_style).pack(pady=2, padx=30, anchor=tk.W)

            # 疫苗信息
            info_menu = tk.Label(menu_frame, text='疫苗信息',
                                font=('SimHei', 11),
                                bg='#E8E8E8', fg='#555555')
            info_menu.pack(anchor=tk.W, padx=20)

            tk.Button(menu_frame, text='信息查询',
                     command=lambda: [self.set_page('基础数据管理 -> 疫苗信息 -> 信息查询'), self.show_content('vaccine_search')],
                     **menu_button_style).pack(pady=2, padx=30, anchor=tk.W)
            tk.Button(menu_frame, text='信息修改',
                     command=lambda: [self.set_page('基础数据管理 -> 疫苗信息 -> 信息修改'), self.show_content('vaccine_edit')],
                     **menu_button_style).pack(pady=2, padx=30, anchor=tk.W)

            # 主体档案
            entity_menu = tk.Label(menu_frame, text='主体档案',
                                  font=('SimHei', 11),
                                  bg='#E8E8E8', fg='#555555')
            entity_menu.pack(anchor=tk.W, padx=20)

            tk.Button(menu_frame, text='统一管理',
                     command=lambda: [self.set_page('基础数据管理 -> 主体档案 -> 统一管理'), self.show_content('entity_archive')],
                     **menu_button_style).pack(pady=2, padx=30, anchor=tk.W)

            # 疫苗类别
            cat_menu = tk.Label(menu_frame, text='疫苗类别',
                              font=('SimHei', 11),
                              bg='#E8E8E8', fg='#555555')
            cat_menu.pack(anchor=tk.W, padx=20)

            tk.Button(menu_frame, text='类别定义',
                     command=lambda: [self.set_page('基础数据管理 -> 疫苗类别 -> 类别定义'), self.show_content('cat_define')],
                     **menu_button_style).pack(pady=2, padx=30, anchor=tk.W)

            tk.Frame(menu_frame, height=2, bg='#CCCCCC').pack(fill=tk.X, pady=10)

        # ====== 业务管理 ======
        if 'business' in perms:
            business_menu = tk.Label(menu_frame, text='业务管理',
                                   font=('SimHei', 12, 'bold'),
                                   bg='#E8E8E8', fg='#1E90FF')
            business_menu.pack(pady=(10, 5), anchor=tk.W, padx=10)

            # 业务按钮
            business_buttons = [
                ('出库登记', '业务管理 -> 出库管理 -> 出库登记', 'outbound'),
                ('有效期提醒', '业务管理 -> 有效期管理 -> 有效期提醒', 'expiry_remind'),
                ('过期处理', '业务管理 -> 有效期管理 -> 过期产品处理', 'expiry_handle'),
                ('库存清单', '业务管理 -> 库存管理 -> 库存清单', 'inventory_list'),
                ('库存预警', '业务管理 -> 库存管理 -> 库存预警', 'inventory_warning'),
                ('库存统计', '业务管理 -> 统计报表 -> 库存统计', 'inventory_stat'),
            ]

            for btn_text, page_name, content_type in business_buttons:
                tk.Button(menu_frame, text=btn_text,
                         command=lambda pn=page_name, ct=content_type: [self.set_page(pn), self.show_content(ct)],
                         **menu_button_style).pack(pady=2, padx=20, anchor=tk.W)

            tk.Frame(menu_frame, height=2, bg='#CCCCCC').pack(fill=tk.X, pady=10)

            # ====== 报表中心 ======
            report_menu = tk.Label(menu_frame, text='📊 报表中心',
                                  font=('SimHei', 12, 'bold'),
                                  bg='#E8E8E8', fg='#1E90FF')
            report_menu.pack(pady=(10, 5), anchor=tk.W, padx=10)

            tk.Button(menu_frame, text='统一报表界面',
                     command=lambda: [self.set_page('报表中心 -> 统一报表界面'), self.show_content('report_center')],
                     **menu_button_style).pack(pady=2, padx=20, anchor=tk.W)

            tk.Frame(menu_frame, height=2, bg='#CCCCCC').pack(fill=tk.X, pady=10)

        # ====== 采购计划与订单 ======
        if 'purchase' in perms:
            purchase_menu = tk.Label(menu_frame, text='采购计划与订单',
                                   font=('SimHei', 12, 'bold'),
                                   bg='#E8E8E8', fg='#1E90FF')
            purchase_menu.pack(pady=(10, 5), anchor=tk.W, padx=10)

            tk.Button(menu_frame, text='按需申购',
                     command=lambda: [self.set_page('采购计划与订单 -> 按需申购'), self.show_content('purchase_request')],
                     **menu_button_style).pack(pady=2, padx=20, anchor=tk.W)

            tk.Frame(menu_frame, height=2, bg='#CCCCCC').pack(fill=tk.X, pady=10)

        # ====== 系统管理 ======
        if 'system' in perms:
            system_menu = tk.Label(menu_frame, text='系统管理',
                                  font=('SimHei', 12, 'bold'),
                                  bg='#E8E8E8', fg='#1E90FF')
            system_menu.pack(pady=(10, 5), anchor=tk.W, padx=10)

            system_buttons = [
                ('权限管理', '系统管理 -> 权限管理', 'permission_mgmt'),
                ('操作日志', '系统管理 -> 操作日志', 'logs'),
                ('数据备份', '系统管理 -> 数据备份', 'backup'),
                ('数据导出', '系统管理 -> 数据导出', 'export'),
                ('系统设置', '系统管理 -> 系统设置', 'settings'),
            ]

            for btn_text, page_name, content_type in system_buttons:
                tk.Button(menu_frame, text=btn_text,
                         command=lambda pn=page_name, ct=content_type: [self.set_page(pn), self.show_content(ct)],
                         **menu_button_style).pack(pady=2, padx=20, anchor=tk.W)

        # 退出
        tk.Button(menu_frame, text='🚪 退出系统', command=self._logout,
                 **exit_button_style).pack(pady=(20, 10), padx=20, anchor=tk.W)
    
    def set_page(self, page_name):
        if self.current_page_var:
            self.current_page_var.set(page_name)
    
    def clear_content(self):
        if self.current_content:
            for widget in self.current_content.winfo_children():
                widget.destroy()
    
    def show_content(self, content_type):
        self.clear_content()

        try:
            from ui.pages import render_page
            render_page(content_type, self.current_content, self.service)
        except Exception as e:
            print(f"加载页面 {content_type} 失败：{e}")
            error_label = tk.Label(self.current_content, 
                                  text=f'页面加载失败：{content_type}\n错误：{str(e)}',
                                  font=('SimHei', 14),
                                  fg='#FF0000',
                                  bg='#FFFFFF')
            error_label.pack(pady=50)


    def _logout(self):
        # 退出主窗口，回到登录界面
        if self.root:
            self.root.destroy()
        if self.on_logout:
            self.on_logout()


# 登录窗口
class LoginWindow:
    
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.root = None
    
    def show(self):
        self.root = tk.Tk()
        self.root.title('疫苗管理系统')
        self.root.geometry('1000x600')
        self.root.resizable(False, False)
        
        # 使用白色背景
        self.root.configure(bg='white')

        login_frame = tk.Frame(self.root, bg='white', bd=0, relief=tk.RAISED, padx=40, pady=40)
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=450, height=500)
        
        # 标题
        title = tk.Label(login_frame, text='疫苗管理系统', 
                        font=('Roboto', 24, 'bold'), 
                        fg='#333333', bg='white')
        title.pack(pady=30, anchor=tk.CENTER)

        user_frame = tk.Frame(login_frame, bg='white')
        user_frame.pack(pady=15, fill=tk.X)
        user_entry_frame = tk.Frame(user_frame, bg='white', bd=1, 
                                  relief=tk.SUNKEN, 
                                  highlightbackground='#E0E0E0',
                                  highlightcolor='#E0E0E0',
                                  highlightthickness=1)
        user_entry_frame.pack(fill=tk.X, pady=5)
        
        user_icon = tk.Label(user_entry_frame, text='👤', 
                           font=('Arial', 14), 
                           bg='white', fg='#999999')
        user_icon.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(
            user_entry_frame,
            textvariable=self.username_var,
            font=('Roboto', 14, 'normal'),
            bd=0,
            bg='white',
            fg='#333333',
        )
        username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=10, padx=(0, 5))

        pwd_frame = tk.Frame(login_frame, bg='white')
        pwd_frame.pack(pady=15, fill=tk.X)
        pwd_entry_frame = tk.Frame(pwd_frame, bg='white', bd=1,
                                 relief=tk.SUNKEN,
                                 highlightbackground='#E0E0E0',
                                 highlightcolor='#E0E0E0',
                                 highlightthickness=1)
        pwd_entry_frame.pack(fill=tk.X, pady=5)
        
        pwd_icon = tk.Label(pwd_entry_frame, text='🔒',
                          font=('Arial', 14),
                          bg='white', fg='#999999')
        pwd_icon.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.password_var = tk.StringVar()
        self.pwd_visible = False
        pwd_entry = tk.Entry(pwd_entry_frame,
                           textvariable=self.password_var,
                           show='*',
                           font=('Roboto', 14, 'normal'),
                           bd=0, bg='white', fg='#333333')
        pwd_entry.pack(side=tk.LEFT, fill=tk.X, pady=10)

        def toggle_pwd_visibility():
            self.pwd_visible = not self.pwd_visible
            if self.pwd_visible:
                pwd_entry.config(show='')
                toggle_btn.config(text='👁️')
            else:
                pwd_entry.config(show='*')
                toggle_btn.config(text='👁️‍🗨️')
        
        toggle_btn = tk.Button(pwd_entry_frame, text='👁️‍🗨️',
                             font=('Arial', 12),
                             bg='white', fg='#999999',
                             bd=0, cursor='hand2',
                             command=toggle_pwd_visibility)
        toggle_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        remember_frame = tk.Frame(login_frame, bg='white')
        remember_frame.pack(pady=15, anchor=tk.W)
        self.remember_var = tk.BooleanVar()
        remember_checkbox = tk.Checkbutton(remember_frame, text='记住我',
                                         variable=self.remember_var,
                                         bg='white',
                                         font=('Roboto', 12, 'normal'),
                                         fg='#333333',
                                         selectcolor='white')
        remember_checkbox.pack(anchor=tk.W)

        login_button = tk.Button(login_frame, text='登录',
                               font=('Roboto', 16, 'bold'),
                               bg='#FF9900', fg='white',
                               bd=0, cursor='hand2',
                               command=self.login,
                               activebackground='#E68A00',
                               activeforeground='white')
        login_button.pack(pady=20, fill=tk.X, ipady=10)

        footer_frame = tk.Frame(login_frame, bg='white')
        footer_frame.pack(pady=30, fill=tk.X)
        footer_label = tk.Label(footer_frame,
                              text='© 2026 疫苗管理系统 版权所有',
                              font=('Roboto', 10, 'normal'),
                              fg='#999999',
                              bg='white',
                              justify=tk.CENTER)
        footer_label.pack(fill=tk.X)

        self.root.mainloop()
    
    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        result = vaccine_service.authenticate(username, password)
        
        if result['success']:
            self.root.destroy()
            if self.on_login_success:
                self.on_login_success(result['user'])
        else:
            messagebox.showerror('错误', result['message'])
