import sys

from ui.app import VaccineManagementApp, LoginWindow
from services.vaccine_service import vaccine_service


def launch_login():
    # 启动登录窗口，登录成功后进入主界面

    def on_login_success(user_info):
        print(f"登录成功：{user_info['username']} ({user_info['role']})")
        print(f"权限：{', '.join(user_info.get('permissions', []))}")
        app = VaccineManagementApp(current_user=user_info, on_logout=launch_login)
        app.run_main()

    if vaccine_service.initial_admin_password:
        from tkinter import messagebox
        messagebox.showwarning(
            '首次运行初始化',
            '已创建本地管理员账号。\n\n'
            f'用户名：admin\n'
            f'初始密码：{vaccine_service.initial_admin_password}\n\n'
            '该密码只显示一次，请登录后立即在“权限管理”中修改。',
        )
        vaccine_service.initial_admin_password = None

    login_window = LoginWindow(on_login_success)
    login_window.show()


def main():
    launch_login()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n启动失败：{e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
