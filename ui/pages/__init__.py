def render_page(content_type, parent, service):
    page_map = {
        # === 入库管理 ===
        'single_inventory': 'inventory_pages',
        'batch_inventory': 'inventory_pages',
        'inventory_audit': 'inventory_pages',
        'inventory_doc': 'inventory_pages',
        'inventory_record': 'inventory_pages',

        # === 疫苗信息 ===
        'vaccine_search': 'vaccine_pages',
        'vaccine_edit': 'vaccine_pages',

        # === 主体档案 ===
        'entity_archive': 'manufacturer_pages',

        # === 类别定义 ===
        'cat_define': 'category_pages',

        # === 业务管理 ===
        'outbound': 'business_pages',
        'expiry_remind': 'business_pages',
        'expiry_handle': 'business_pages',
        'inventory_list': 'business_pages',
        'inventory_warning': 'business_pages',
        'inventory_stat': 'report_pages',

        # === 报表中心 ===
        'report_center': 'report_pages',

        # === 采购管理 ===
        'purchase_request': 'purchase_pages',

        # === 系统管理 ===
        'permission_mgmt': 'system_pages',
        'logs': 'system_pages',
        'backup': 'system_pages',
        'export': 'system_pages',
        'settings': 'system_pages',
    }

    if content_type in page_map:
        module_name = page_map[content_type]

        try:
            module = __import__(f'ui.pages.{module_name}', fromlist=['render'])

            render_func = getattr(module, f'render_{content_type}', None)
            if render_func:
                render_func(parent, service)
            else:
                if hasattr(module, 'render'):
                    module.render(content_type, parent, service)

        except ImportError as e:
            print(f"无法导入模块 {module_name}：{e}")
            _show_error_page(parent, f"模块未实现：{module_name}")
    else:
        _show_error_page(parent, f"未知页面类型：{content_type}")


def _show_error_page(parent, message):
    import tkinter as tk
    error_label = tk.Label(
        parent,
        text=message,
        font=('SimHei', 16),
        fg='#FF0000',
        bg='#FFFFFF'
    )
    error_label.pack(pady=50)
