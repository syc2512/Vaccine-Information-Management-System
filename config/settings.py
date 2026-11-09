import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, 'data')

DATA_FILES = {
    'vaccines': 'vaccines.json',
    'manufacturers': 'manufacturers.json',
    'categories': 'categories.json',
    'cold_storage': 'cold_storage.json',
    'orders': 'orders.json'
}

DEFAULT_SETTINGS = {
    'system_name': '疫苗管理系统',
    'min_stock': 10,
    'expiry_warning_days': 30,
    'enable_popup_alert': True,
    'date_format': 'YYYY-MM-DD',
    'max_log_entries': 1000,
    'auto_clean_expired': False,
    'force_outbound_audit': False,
}

DATABASE_FILENAME = 'vaccine_system.db'

DEFAULT_ROLES = [
    {
        'id': 1,
        'name': '超级管理员',
        'permissions': ['basic_data', 'business', 'purchase', 'system'],
        'description': '拥有系统所有权限',
    },
    {
        'id': 2,
        'name': '基础数据管理员',
        'permissions': ['basic_data'],
        'description': '负责入库、疫苗信息、主体档案和类别管理',
    },
    {
        'id': 3,
        'name': '业务管理员',
        'permissions': ['business'],
        'description': '负责出库、效期、库存和报表业务',
    },
    {
        'id': 4,
        'name': '采购管理员',
        'permissions': ['purchase'],
        'description': '负责采购计划与订单管理',
    },
    {
        'id': 5,
        'name': '系统管理员',
        'permissions': ['system'],
        'description': '负责用户、日志、备份和系统设置',
    },
    {
        'id': 6,
        'name': '普通操作员',
        'permissions': ['basic_data', 'business'],
        'description': '可进行基础数据管理和业务操作',
    },
]

VACCINE_TYPES = [
    '',
    '灭活疫苗（死疫苗）',
    '减毒活疫苗',
    '类毒素疫苗',
    '亚单位 / 组分疫苗',
    '重组蛋白疫苗',
    '多糖疫苗与结合疫苗',
    '病毒载体疫苗',
    '核酸疫苗（DNA/RNA 疫苗）',
    '病毒样颗粒疫苗 (VLP)',
    '其他疫苗'
]

TEMP_TYPE_MAP = {
    '冷藏': ('refrigerator', '2-8℃'),
    '冷冻': ('freezer', '-20℃'),
}

STORAGE_KEYWORDS = [
    '避光保存', '不可倒置', '防潮', '防热', 
    '防震', '轻拿轻放', '密封保存', '避免阳光直射', 
    '不可冷冻', '不可冷藏'
]

MAX_LOG_ENTRIES = 1000

ALERT_THRESHOLDS = {
    'low_stock': 10
}
