import os
import re
import datetime
import hmac

from config.settings import DEFAULT_ROLES, DEFAULT_SETTINGS
from utils.data_repository import repository as default_repository
from utils.security import (
    generate_initial_password,
    hash_password,
    is_password_hash,
    validate_new_password,
    verify_password,
)


class VaccineService:

    def __init__(self, repository=None):
        self.repository = repository or default_repository
        self.current_user = None
        self.initial_admin_password = None
        self._load_all_data()

    def _load_all_data(self):
        self.vaccines = self.repository.load_vaccines()
        self.manufacturers = self.repository.load_manufacturers()
        self.categories = self.repository.load_categories()
        self.cold_storages = self.repository.load_cold_storage()
        self.orders = self.repository.load_orders()
        self.outbound_records = self.repository.load_outbound_records()
        self.inventory_records = self.repository.load_inventory_records()
        self.users = self.repository.load_users()
        self.roles = self.repository.load_roles()
        self.settings = self.repository.load_settings()
        self.suppliers = self.repository.load_suppliers()
        self.purchase_requests = self.repository.load_purchase_requests()
        self.temp_humidity_records = self.repository.load_temp_humidity_records()
        self.recipient_units = self.repository.load_recipient_units()
        self.operation_logs = self.repository.load_operation_logs()

        self._sync_manufacturers_from_vaccines()
        self._sync_categories_from_vaccines()
        self._migrate_historical_data()
        self._migrate_passwords()
        self._ensure_bootstrap_data()

        self.id_counter = self.get_next_id()

    def authenticate(self, username, password):
        if not username or not password:
            return {'success': False, 'user': None, 'message': '请输入用户名和密码'}

        for user in (self.users or []):
            if user.get('username') == username:
                if user.get('status') != 'active':
                    return {'success': False, 'user': None, 'message': '该账号已被禁用，请联系管理员'}
                stored_password = user.get('password', '')
                password_valid = verify_password(password, stored_password)
                if not password_valid and not is_password_hash(stored_password):
                    password_valid = hmac.compare_digest(
                        str(stored_password).encode('utf-8'),
                        password.encode('utf-8'),
                    )
                    if password_valid:
                        user['password'] = hash_password(password)
                        self.repository.save_users(self.users)

                if password_valid:
                    permissions = []
                    role_name = user.get('role', '')
                    for role in (self.roles or []):
                        if role.get('name') == role_name:
                            permissions = role.get('permissions', [])
                            break
                    user_info = {
                        'id': user.get('id'),
                        'username': user.get('username'),
                        'role': role_name,
                        'permissions': permissions
                    }
                    self.set_current_user(user_info)
                    return {'success': True, 'user': user_info, 'message': '登录成功'}
                else:
                    return {'success': False, 'user': None, 'message': '用户名或密码错误'}

        return {'success': False, 'user': None, 'message': '用户名或密码错误'}

    def set_current_user(self, user_info):
        self.current_user = dict(user_info) if user_info else None

    def has_permission(self, permission):
        if not self.current_user:
            return False
        return permission in self.current_user.get('permissions', [])

    def _migrate_passwords(self):
        changed = False
        for user in self.users or []:
            password = user.get('password')
            if password and not is_password_hash(password):
                user['password'] = hash_password(str(password))
                changed = True
        if changed:
            self.repository.save_users(self.users)

    def _ensure_bootstrap_data(self):
        if not self.roles:
            self.roles = [dict(role) for role in DEFAULT_ROLES]
            self.repository.save_roles(self.roles)

        active_users = [user for user in (self.users or []) if user.get('status') == 'active']
        if active_users:
            return

        admin_password = os.getenv('VACCINE_ADMIN_PASSWORD', '').strip()
        if admin_password:
            validate_new_password(admin_password)
        else:
            admin_password = generate_initial_password()
            self.initial_admin_password = admin_password

        admin = {
            'id': max((user.get('id', 0) for user in (self.users or [])), default=0) + 1,
            'username': 'admin',
            'password': hash_password(admin_password),
            'role': '超级管理员',
            'status': 'active',
        }
        if not self.users:
            self.users = []
        self.users.append(admin)
        self.repository.save_users(self.users)

    def create_user(self, username, password, role):
        username = str(username or '').strip()
        role = str(role or '').strip()
        if not username:
            raise ValueError('用户名不能为空')
        if any(user.get('username') == username for user in (self.users or [])):
            raise ValueError('用户名已存在')
        if role not in {item.get('name') for item in (self.roles or [])}:
            raise ValueError('请选择有效角色')
        validate_new_password(password)

        user = {
            'id': max((item.get('id', 0) for item in (self.users or [])), default=0) + 1,
            'username': username,
            'password': hash_password(password),
            'role': role,
            'status': 'active',
        }
        self.users.append(user)
        if not self.save_data():
            self.users.pop()
            raise RuntimeError('用户保存失败')
        self.log_operation(f'添加用户：{username}')
        return user

    def update_user(self, user_id, username, role, password=''):
        target = next(
            (user for user in (self.users or []) if str(user.get('id')) == str(user_id)),
            None,
        )
        if not target:
            raise ValueError('用户不存在')

        username = str(username or '').strip()
        role = str(role or '').strip()
        if not username:
            raise ValueError('用户名不能为空')
        if any(
            user is not target and user.get('username') == username
            for user in (self.users or [])
        ):
            raise ValueError('用户名已存在')
        if role not in {item.get('name') for item in (self.roles or [])}:
            raise ValueError('请选择有效角色')

        previous = dict(target)
        target['username'] = username
        target['role'] = role
        if password:
            validate_new_password(password)
            target['password'] = hash_password(password)

        if not self.save_data():
            target.clear()
            target.update(previous)
            raise RuntimeError('用户保存失败')
        self.log_operation(f'修改用户：{username}')
        return target

    def delete_user(self, user_id):
        target = next(
            (user for user in (self.users or []) if str(user.get('id')) == str(user_id)),
            None,
        )
        if not target:
            raise ValueError('用户不存在')
        if self.current_user and str(self.current_user.get('id')) == str(user_id):
            raise ValueError('不能删除当前登录账号')
        self.users.remove(target)
        if not self.save_data():
            self.users.append(target)
            raise RuntimeError('用户删除失败')
        self.log_operation(f'删除用户：{target.get("username", "")}')

    def get_next_id(self):
        if not self.vaccines:
            return 1
        try:
            ids = []
            for v in self.vaccines:
                vid = v.get('id')
                if isinstance(vid, int):
                    ids.append(vid)
                elif isinstance(vid, str) and vid.isdigit():
                    ids.append(int(vid))
            return max(ids) + 1 if ids else 1
        except Exception:
            return len(self.vaccines) + 1

    def _sync_manufacturers_from_vaccines(self):
        vaccine_manufacturers = set()
        for vaccine in self.vaccines:
            manufacturer = vaccine.get('manufacturer', '').strip()
            if manufacturer and manufacturer not in ['暂无厂家', '无', '-']:
                vaccine_manufacturers.add(manufacturer)

        existing_names = {m['name'] for m in self.manufacturers}

        new_manufacturers_added = 0
        for mf_name in vaccine_manufacturers:
            if mf_name not in existing_names:
                new_mf = {
                    'id': self.get_next_manufacturer_id(),
                    'name': mf_name,
                    'status': 'active'
                }
                self.manufacturers.append(new_mf)
                existing_names.add(mf_name)
                new_manufacturers_added += 1

        if new_manufacturers_added > 0:
            self.repository.save_manufacturers(self.manufacturers)

    def _sync_categories_from_vaccines(self):
        vaccine_categories = set()
        for vaccine in self.vaccines:
            category = vaccine.get('category', '').strip()
            if category and category not in ['', '-', '无']:
                vaccine_categories.add(category)

        existing_names = {c.get('name', '') for c in (self.categories or []) if c.get('name')}

        new_count = 0
        for cat_name in vaccine_categories:
            if cat_name not in existing_names:
                new_cat = {
                    'id': self.get_next_category_id(),
                    'name': cat_name,
                    'description': '从疫苗记录自动同步'
                }
                if not self.categories:
                    self.categories = []
                self.categories.append(new_cat)
                existing_names.add(cat_name)
                new_count += 1

        if new_count > 0:
            self.repository.save_categories(self.categories)

    def _migrate_historical_data(self):
        # 补全缺失的字段
        data_changed = False

        for vaccine in self.vaccines:
            # 1. 补全 入库单号：根据 stock_time / 入库时间 / audit_time 生成
            if '入库单号' not in vaccine or not vaccine.get('入库单号'):
                time_str = (
                    vaccine.get('入库时间') or
                    vaccine.get('stock_time') or
                    vaccine.get('audit_time') or
                    ''
                )
                if time_str:
                    try:
                        dt = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                        time_part = dt.strftime('%Y%m%d%H%M%S')
                    except (ValueError, TypeError):
                        time_part = '20260101000000'
                else:
                    time_part = '20260101000000'

                vaccine['入库单号'] = f'RK{time_part}{vaccine.get("id", 0)}'
                data_changed = True

            # 2. 补全 storage_id：缺失或空字符串均设为 "待分配"
            storage_id = vaccine.get('storage_id')
            if storage_id is None or storage_id == '':
                vaccine['storage_id'] = '待分配'
                data_changed = True

            # 3. 补全 审核状态：仅在字段缺失或值为空时才补
            if '审核状态' not in vaccine or not vaccine.get('审核状态'):
                if vaccine.get('status') == 'in_stock':
                    vaccine['审核状态'] = '已审核'
                else:
                    vaccine['审核状态'] = '待审核'
                data_changed = True

            # 4. 补全 入库时间：优先用 stock_time / audit_time，都没有用当前时间
            if '入库时间' not in vaccine or not vaccine.get('入库时间'):
                time_val = (
                    vaccine.get('stock_time') or
                    vaccine.get('audit_time') or
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                vaccine['入库时间'] = time_val
                data_changed = True

        if data_changed:
            self.save_data()

    def log_operation(self, user=None, action=None):
        if action is None:
            action = user
            user = (self.current_user or {}).get('username', 'system')
        log_entry = {
            'user': user or 'system',
            'action': str(action or ''),
            'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.operation_logs.append(log_entry)
        max_entries = int(self.settings.get('max_log_entries', 1000))
        if len(self.operation_logs) > max_entries:
            self.operation_logs = self.operation_logs[-max_entries:]
        return self.repository.save_operation_logs(self.operation_logs)

    def save_data(self):
        stores = {
            'vaccines': self.vaccines or [],
            'manufacturers': self.manufacturers or [],
            'categories': self.categories or [],
            'cold_storage': self.cold_storages or [],
            'orders': self.orders or [],
            'outbound_records': self.outbound_records or [],
            'inventory_records': self.inventory_records or [],
            'users': self.users or [],
            'roles': self.roles or [],
            'suppliers': self.suppliers or [],
            'purchase_requests': self.purchase_requests or [],
            'temp_humidity_records': self.temp_humidity_records or [],
            'recipient_units': self.recipient_units or [],
            'operation_logs': self.operation_logs or [],
        }
        return self.repository.save_snapshot(stores, settings=self.settings)

    def reload_data(self):
        self._load_all_data()

    def get_next_manufacturer_id(self):
        if not self.manufacturers:
            return 1
        return max(m['id'] for m in self.manufacturers) + 1

    def get_next_category_id(self):
        if not self.categories:
            return 1
        return max(c['id'] for c in self.categories) + 1
    

    # ==================== 疫苗入库 ====================

    def add_vaccine(self, name, category, production_date,
                   expiry_date, manufacturer, quantity,
                   batch_number, vaccine_type='refrigerator',
                   storage_id=None, remark=''):
        from services.validators import validate_vaccine_data
        valid, msg = validate_vaccine_data({
            'name': name,
            'category': category,
            'production_date': production_date,
            'expiry_date': expiry_date,
            'manufacturer': manufacturer,
            'quantity': quantity,
            'batch_number': batch_number
        })
        if not valid:
            raise ValueError(f'数据校验失败：\n{msg}')

        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        入库单号 = f'RK{current_time}{self.id_counter}'

        for existing_vaccine in self.vaccines:
            if (existing_vaccine['batch_number'] == batch_number and
                existing_vaccine['name'] == name and
                existing_vaccine['category'] == category and
                existing_vaccine['manufacturer'] == manufacturer and
                existing_vaccine['expiry_date'] == expiry_date and
                existing_vaccine['status'] == 'pending'):
                existing_vaccine['quantity'] += quantity
                existing_vaccine['入库时间'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if remark:
                    existing_vaccine['remark'] = remark
                self.save_data()
                return existing_vaccine

        vaccine = {
            'id': self.id_counter,
            'name': name,
            'category': category,
            'production_date': production_date,
            'expiry_date': expiry_date,
            'manufacturer': manufacturer,
            'quantity': quantity,
            'batch_number': batch_number,
            'vaccine_type': vaccine_type,
            'storage_id': storage_id,
            'remark': remark,
            '入库单号': 入库单号,
            '审核状态': '待审核',
            '入库时间': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'pending'
        }
        self.vaccines.append(vaccine)
        self.id_counter += 1

        if manufacturer and manufacturer not in ['暂无厂家', '无', '-']:
            existing_names = {m['name'] for m in self.manufacturers}
            if manufacturer not in existing_names:
                new_mf = {
                    'id': self.get_next_manufacturer_id(),
                    'name': manufacturer,
                    'status': 'active'
                }
                self.manufacturers.append(new_mf)
                self.repository.save_manufacturers(self.manufacturers)

        self.save_data()
        return vaccine
    

    def batch_add_vaccines(self, file_path):
        added_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue

                fields = line.split(',')
                if len(fields) < 6:
                    continue

                vaccine_id = fields[0].strip()
                name = fields[1].strip()
                category = fields[2].strip() if len(fields) > 2 else ''
                prod_date = fields[3].strip() if len(fields) > 3 else '2026-01-01'
                expiry_date = fields[4].strip() if len(fields) > 4 else '2026-12-31'
                manufacturer = fields[5].strip() if len(fields) > 5 else ''
                quantity = int(fields[6].strip()) if len(fields) > 6 and fields[6].strip().isdigit() else 1
                batch_number = fields[7].strip() if len(fields) > 7 else ''
                vaccine_type = fields[8].strip() if len(fields) > 8 else '冷藏'
                storage_id = fields[9].strip() if len(fields) > 9 else ''
                remark = fields[10].strip() if len(fields) > 10 else ''

                existing_vaccine = None
                for v in self.vaccines:
                    if (v.get('batch_number') == batch_number and
                        v.get('name') == name and
                        v.get('category') == category and
                        v.get('status') == 'pending'):
                        existing_vaccine = v
                        break

                if existing_vaccine:
                    existing_vaccine['quantity'] = existing_vaccine.get('quantity', 0) + quantity
                    if '入库单号' not in existing_vaccine or not existing_vaccine['入库单号']:
                        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                        existing_vaccine['入库单号'] = f'RK{current_time}{vaccine_id}'
                    if '入库时间' not in existing_vaccine:
                        existing_vaccine['入库时间'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                else:
                    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                    new_vaccine = {
                        'id': vaccine_id,
                        'name': name,
                        'category': category,
                        'production_date': prod_date,
                        'expiry_date': expiry_date,
                        'manufacturer': manufacturer,
                        'quantity': quantity,
                        'batch_number': batch_number,
                        'vaccine_type': vaccine_type,
                        'storage_id': storage_id,
                        'remark': remark,
                        'status': 'pending',
                        'stock_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        '入库单号': f'RK{current_time}{vaccine_id}',
                        '入库时间': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    self.vaccines.append(new_vaccine)

                added_count += 1

            self.save_data()
            return f'成功导入 {added_count} 条疫苗记录'

        except Exception as e:
            return f'导入失败：{str(e)}'

    # ==================== 疫苗出库 ====================

    def register_outbound(self, vaccine_id, quantity, recipient, purpose):
        for vaccine in self.vaccines:
            if vaccine['id'] == vaccine_id and vaccine['status'] == 'in_stock':
                current_quantity = vaccine.get('quantity', 1)
                if current_quantity < quantity:
                    return False, '库存不足'

                vaccine['quantity'] = current_quantity - quantity
                if vaccine['quantity'] == 0:
                    vaccine['status'] = 'out_stock'

                self.save_data()
                return True, '出库成功'
        return False, '疫苗不存在或已出库'

    # ==================== 入库审核 ====================

    def approve_vaccine(self, vaccine_id):
        for vaccine in self.vaccines:
            if vaccine['id'] == vaccine_id and vaccine.get('审核状态') == '待审核':
                vaccine['审核状态'] = '已审核'
                vaccine['status'] = 'in_stock'
                self.save_data()
                return True
        return False

    def reject_vaccine(self, vaccine_id):
        for vaccine in self.vaccines:
            if vaccine['id'] == vaccine_id and vaccine.get('status') == 'pending':
                vaccine['status'] = 'rejected'
                self.save_data()
                return True
        return False

    def get_pending_vaccines(self):
        return [v for v in self.vaccines if v.get('审核状态') == '待审核']

    # ==================== 库存查询 ====================

    def get_stock_list(self, category=None,
                      manufacturer=None):
        result = []
        for vaccine in self.vaccines:
            if vaccine['status'] == 'in_stock':
                if category and vaccine['category'] != category:
                    continue
                if manufacturer and vaccine['manufacturer'] != manufacturer:
                    continue
                result.append(vaccine)
        return result

    def get_fifo_vaccines(self, vaccine_name):
        vaccines = [v for v in self.vaccines
                   if v.get('name') == vaccine_name and v.get('status') == 'in_stock']
        vaccines.sort(key=lambda x: x.get('expiry_date', ''))
        return vaccines

    def get_expiring_vaccines(self, days=30):
        today = datetime.date.today()
        expiring = []
        for vaccine in self.vaccines:
            if vaccine['status'] == 'in_stock':
                try:
                    expiry = datetime.date.fromisoformat(vaccine['expiry_date'])
                    if 0 <= (expiry - today).days <= days:
                        expiring.append(vaccine)
                except (ValueError, TypeError):
                    pass
        return expiring

    def get_expired_vaccines(self):
        today = datetime.date.today()
        expired = []
        for vaccine in self.vaccines:
            if vaccine['status'] in ['in_stock', 'expired']:
                try:
                    expiry = datetime.date.fromisoformat(vaccine['expiry_date'])
                    if (expiry - today).days < 0:
                        expired.append(vaccine)
                except (ValueError, TypeError):
                    pass
        return expired

    def cancel_expired(self, vaccine_ids=None, reason='', disposal_method=''):
        today = datetime.date.today()
        count = 0

        if vaccine_ids is None:
            for vaccine in self.vaccines:
                if vaccine['status'] == 'in_stock':
                    try:
                        expiry = datetime.date.fromisoformat(vaccine['expiry_date'])
                        if (expiry - today).days < 0:
                            vaccine['status'] = 'expired'
                            count += 1
                    except (ValueError, TypeError):
                        pass
        else:
            for vaccine_id in vaccine_ids:
                for vaccine in self.vaccines:
                    if vaccine['id'] == vaccine_id and vaccine['status'] in ['in_stock', 'expired']:
                        if '注销记录' not in vaccine:
                            vaccine['注销记录'] = []

                        vaccine['注销记录'].append({
                            '注销时间': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            '注销原因': reason,
                            '处理方式': disposal_method,
                            '处理人': 'admin',
                            '注销单号': f'CANCEL{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'
                        })

                        vaccine['status'] = 'cancelled'
                        count += 1

        if count > 0:
            self.save_data()
        return count

    # ==================== 冷库管理 ====================

    def recommend_storage(self, vaccine_type):
        type_map = {
            'freezer': ('freezer', '-20℃冷冻'),
            '-20℃冷冻': ('freezer', '-20℃冷冻'),
            'refrigerator': ('refrigerator', '2-8℃冷藏'),
            '冷藏': ('refrigerator', '2-8℃冷藏'),
        }

        required_type, temp_desc = type_map.get(vaccine_type, ('refrigerator', '2-8℃冷藏'))

        available_storages = [
            s for s in self.cold_storages
            if s['type'] == required_type and s['status'] == 'available'
        ]

        if available_storages:
            available_storages.sort(key=lambda x: x['capacity'], reverse=True)
            return {
                'success': True,
                'recommendation': available_storages[0],
                'alternatives': available_storages[1:],
                'temp_desc': temp_desc
            }
        else:
            return {
                'success': False,
                'message': f'当前没有可用的{temp_desc}库位',
                'temp_desc': temp_desc
            }

    def lock_storage(self, storage_id, quantity):
        for storage in self.cold_storages:
            if storage['id'] == storage_id:
                if storage['used'] + quantity <= storage['capacity']:
                    storage['used'] += quantity
                    if storage['used'] >= storage['capacity']:
                        storage['status'] = 'full'
                    self.repository.save_cold_storage(self.cold_storages)
                    return True
                return False
        return False
    

    # ==================== 统计预警 ====================

    def get_inventory_alerts(self, low_threshold=None):
        if low_threshold is None:
            low_threshold = DEFAULT_SETTINGS.get('min_stock', 10)

        alerts = {'low_stock': []}

        for vaccine in self.vaccines:
            if vaccine.get('status') != 'in_stock':
                continue

            try:
                qty = vaccine.get('quantity', 0)
                if isinstance(qty, str):
                    qty = int(qty) if qty.isdigit() else 0

                if qty <= low_threshold and qty >= 0:
                    alerts['low_stock'].append({
                        'id': vaccine.get('id', ''),
                        'name': vaccine.get('name', '未知'),
                        'category': vaccine.get('category', '-'),
                        'manufacturer': vaccine.get('manufacturer', '-'),
                        'batch_number': vaccine.get('batch_number', '-'),
                        'production_date': vaccine.get('production_date', '-'),
                        'expiry_date': vaccine.get('expiry_date', '-'),
                        'quantity': qty,
                        'vaccine_type': vaccine.get('vaccine_type', '-')
                    })
            except Exception:
                continue

        return alerts

    def get_inventory_records(self, start_date=None, end_date=None,
                             manufacturer=None, vaccine_name=None):
        records = []
        for vaccine in self.vaccines:
            if start_date:
                vaccine_date = vaccine.get('入库时间', '').split(' ')[0]
                if vaccine_date < start_date:
                    continue
            if end_date:
                vaccine_date = vaccine.get('入库时间', '').split(' ')[0]
                if vaccine_date > end_date:
                    continue
            if manufacturer and vaccine.get('manufacturer') != manufacturer:
                continue
            if vaccine_name and vaccine.get('name') != vaccine_name:
                continue
            records.append(vaccine)
        return records

    def generate_inventory_pdf(self, vaccine_id, output_path='inventory_report'):
        vaccine = None
        for v in self.vaccines:
            if str(v.get('id')) == str(vaccine_id):
                vaccine = v
                break

        if not vaccine:
            return '未找到对应的疫苗记录'

        try:
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>疫苗入库单据</title>
    <style>
        body {{ font-family: SimHei, Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .title {{ font-size: 24px; font-weight: bold; color: #333; }}
        .doc-info {{ margin-top: 10px; color: #666; }}
        .table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .table th, .table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        .table th {{ background-color: #f5f5f5; font-weight: bold; }}
        .footer {{ margin-top: 40px; text-align: center; color: #999; font-size: 12px; }}
        .highlight {{ color: #FF0000; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="title">疫苗入库单据</div>
        <div class="doc-info">单据编号: RK{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}</div>
        <div class="doc-info">生成时间: {datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</div>
    </div>

    <table class="table">
        <tr><th>疫苗编号</th><td>{vaccine.get('id', '-')}</td></tr>
        <tr><th>疫苗名称</th><td>{vaccine.get('name', '-')}</td></tr>
        <tr><th>类别</th><td>{vaccine.get('category', '-')}</td></tr>
        <tr><th>生产厂家</th><td>{vaccine.get('manufacturer', '-')}</td></tr>
        <tr><th>生产日期</th><td>{vaccine.get('production_date', '-')}</td></tr>
        <tr><th>有效期至</th><td class="highlight">{vaccine.get('expiry_date', '-')}</td></tr>
        <tr><th>批号</th><td>{vaccine.get('batch_number', '-')}</td></tr>
        <tr><th>数量（剂）</th><td>{vaccine.get('quantity', 0)}</td></tr>
        <tr><th>疫苗类型</th><td>{vaccine.get('vaccine_type', '冷藏')}</td></tr>
        <tr><th>存储位置</th><td>{vaccine.get('storage_id', '-')}</td></tr>
        <tr><th>入库时间</th><td>{vaccine.get('stock_time', '-')}</td></tr>
        <tr><th>备注</th><td>{vaccine.get('remark', '-')}</td></tr>
    </table>

    <div class="footer">
        <p>&copy; 2025 疫苗管理系统</p>
    </div>
</body>
</html>
"""

            filename = f"{output_path}_{vaccine_id}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return f'单据已生成：{filename}\n请使用浏览器打开并打印为PDF格式'

        except Exception as e:
            return f'生成失败：{str(e)}'




    # ==================== 出库管理增强 ====================

    def _load_recipient_units(self):
        if not hasattr(self, 'recipient_units'):
            self.recipient_units = self.repository.load_recipient_units()
        return self.recipient_units

    def get_recipient_units(self, unit_type=None):
        units = self._load_recipient_units()
        if unit_type:
            units = [u for u in units if u.get('type') == unit_type and u.get('status') == 'active']
        else:
            units = [u for u in units if u.get('status') == 'active']
        return units

    def get_recipient_unit_by_id(self, unit_id):
        units = self._load_recipient_units()
        for u in units:
            if u.get('id') == unit_id:
                return u
        return None

    def add_recipient_unit(self, unit_data):
        units = self._load_recipient_units()
        new_id = max([u['id'] for u in units], default=0) + 1
        unit_data['id'] = new_id
        unit_data['status'] = 'active'
        unit_data['create_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        units.append(unit_data)
        self.recipient_units = units
        self.repository.save_recipient_units(units)
        return unit_data

    def get_fefo_vaccine_batches(self, vaccine_name):
        today = datetime.date.today()
        batches = []

        for v in self.vaccines:
            if (v.get('name') == vaccine_name and
                v.get('status') == 'in_stock' and
                v.get('quantity', 0) > 0):

                batch_info = dict(v)

                try:
                    expiry = datetime.date.fromisoformat(v['expiry_date'])
                    days_left = (expiry - today).days
                    batch_info['days_to_expiry'] = days_left

                    if days_left <= 30:
                        batch_info['expiry_status'] = 'critical'
                        batch_info['expiry_label'] = f'⚠️ 近效期({days_left}天)'
                    elif days_left <= 90:
                        batch_info['expiry_status'] = 'warning'
                        batch_info['expiry_label'] = f'⏰ 注意({days_left}天)'
                    else:
                        batch_info['expiry_status'] = 'normal'
                        batch_info['expiry_label'] = f'✅ 正常({days_left}天)'
                except (ValueError, TypeError):
                    batch_info['days_to_expiry'] = None
                    batch_info['expiry_status'] = 'unknown'
                    batch_info['expiry_label'] = '❓ 效期未知'

                batch_info['temp_requirement'] = self._parse_vaccine_temp(v.get('vaccine_type', ''))

                batches.append(batch_info)

        batches.sort(key=lambda x: x.get('expiry_date', '9999-12-31'))
        return batches

    def _parse_vaccine_temp(self, vaccine_type):
        type = str(vaccine_type).lower().strip()

        if type in ['冷藏', 'refrigerator', '2-8', '2-8℃']:
            return {'range': '2-8℃', 'min': 2, 'max': 8, 'storage_type': 'refrigerator', 'display': '2-8℃冷藏'}
        elif type in ['冷冻', 'freezer', '-20', '-20℃', '-20±5']:
            return {'range': '-20℃±5℃', 'min': -25, 'max': -15, 'storage_type': 'freezer', 'display': '-20℃±5℃冷冻'}
        elif type in ['超低温', 'ultra_low', '-70', '-70℃', '-80']:
            return {'range': '-70~-80℃', 'min': -80, 'max': -70, 'storage_type': 'ultra_low', 'display': '-70℃超低温'}
        else:
            import re
            nums = re.findall(r'-?\d+', type)
            if len(nums) >= 2:
                return {'range': f'{nums[0]}~{nums[1]}℃', 'min': int(nums[0]), 'max': int(nums[1]),
                        'storage_type': 'custom', 'display': f'{nums[0]}~{nums[1]}℃'}
            return {'range': '未知', 'min': None, 'max': None, 'storage_type': 'unknown', 'display': '未指定'}

    def check_temperature_compliance(self, vaccine_id, storage_id=None):
        vaccine = None
        for v in self.vaccines:
            if v.get('id') == vaccine_id or str(v.get('id')) == str(vaccine_id):
                vaccine = v
                break

        if not vaccine:
            return {'compliant': False, 'message': '未找到疫苗信息', 'vaccine_temp': '', 'storage_temp': ''}

        vtemp = self._parse_vaccine_temp(vaccine.get('vaccine_type', ''))

        check_storage_id = storage_id or vaccine.get('storage_id')

        if not check_storage_id:
            return {'compliant': True, 'message': '未分配冷库，请手动确认温度要求',
                    'vaccine_temp': vtemp['display'], 'storage_temp': '未分配'}

        storage = None
        for s in self.cold_storages:
            if s.get('id') == check_storage_id:
                storage = s
                break

        if not storage:
            return {'compliant': False, 'message': f'未找到冷库 {check_storage_id}',
                    'vaccine_temp': vtemp['display'], 'storage_temp': ''}

        stype_match = storage.get('type') == vtemp['storage_type']

        temp_range_ok = True
        if vtemp['min'] is not None and vtemp['max'] is not None:
            stemp_str = storage.get('temp_range', '')
            snums = re.findall(r'-?\d+', stemp_str)
            if len(snums) >= 2:
                s_min, s_max = int(snums[0]), int(snums[1])
                temp_range_ok = (vtemp['min'] >= s_min - 5 and vtemp['max'] <= s_max + 5)

        compliant = stype_match and temp_range_ok

        if compliant:
            return {'compliant': True, 'message': '✅ 温度带符合要求',
                    'vaccine_temp': vtemp['display'], 'storage_temp': storage.get('temp_range', '')}
        else:
            reason = ''
            if not stype_match:
                reason = f'存储类型不匹配(需要{vtemp["storage_type"]}, 当前{storage.get("type")})'
            elif not temp_range_ok:
                reason = f'温度范围不匹配(疫苗需{vtemp["display"]}, 冷库{storage.get("temp_range")})'
            return {'compliant': False, 'message': f'❌ {reason}',
                    'vaccine_temp': vtemp['display'], 'storage_temp': storage.get('temp_range', '')}

    def validate_outbound_quantity(self, vaccine_id, quantity):
        vaccine = None
        for v in self.vaccines:
            if v.get('id') == vaccine_id or str(v.get('id')) == str(vaccine_id):
                vaccine = v
                break

        if not vaccine:
            return (False, 0, '未找到该疫苗')

        if vaccine.get('status') != 'in_stock':
            return (False, 0, '该疫苗当前不在库存中(可能已出库/过期/注销)')

        available = vaccine.get('quantity', 0)

        if quantity <= 0:
            return (False, available, '出库数量必须大于0')

        if quantity > available:
            return (False, available, f'❌ 库存不足！当前仅剩 {available} 支，无法出库 {quantity} 支')

        return (True, available, f'✅ 库存充足，可出库 {quantity} 支（剩余 {available - quantity} 支）')

    def validate_outbound_by_type(self, outbound_type, extra_fields=None):
        extra = extra_fields or {}

        if outbound_type == 'scrap':
            reason = extra.get('remark', '').strip()
            if not reason:
                return (False, '❌ 报废出库必须填写报废原因')
            if len(reason) < 5:
                return (False, '❌ 报废原因至少需要5个字符')
            return (True, '✅ 报废原因已填写')

        elif outbound_type == 'return':
            order_id = extra.get('related_order_id', '').strip()
            if not order_id:
                return (False, '❌ 退回出库必须填写原入库单号/关联单据编号')
            remark = extra.get('remark', '').strip()
            if not remark:
                return (False, '❌ 退回出库必须填写退回原因')
            return (True, '✅ 退回信息完整')

        elif outbound_type == 'vaccination':
            unit_id = extra.get('recipient_unit_id')
            if unit_id:
                unit = self.get_recipient_unit_by_id(unit_id)
                if unit and unit.get('type') != 'vaccination':
                    return (False, f'⚠️ 接种出库建议选择"接种点"类型单位，当前选择的是"{unit.get("type_display", "")}"')
                if unit and unit.get('qualification_status') != 'valid':
                    return (False, f'❌ 领用单位 "{unit.get("name")}" 资质已失效或待审核')
            return (True, '✅ 接种出库校验通过')

        elif outbound_type == 'allocation':
            return (True, '✅ 调拨出库校验通过')

        return (False, f'❌ 未知的出库类型: {outbound_type}')

    def generate_outbound_id(self):
        today = datetime.datetime.now().strftime('%Y%m%d')

        today_count = 0
        for record in self.outbound_records:
            record_time = record.get('outbound_time', '')
            if today in record_time:
                today_count += 1

        seq = today_count + 1
        return f'OUT{today}{seq:04d}'

    def create_outbound_record(self, outbound_data):
        try:
            vaccine_id = outbound_data.get('vaccine_id')
            quantity = outbound_data.get('quantity', 0)
            recipient_unit_id = outbound_data.get('recipient_unit_id')
            outbound_type = outbound_data.get('outbound_type', 'allocation')

            vaccine = None
            for v in self.vaccines:
                if v.get('id') == vaccine_id or str(v.get('id')) == str(vaccine_id):
                    vaccine = v
                    break

            if not vaccine:
                return (False, '❌ 未找到疫苗记录', None)

            valid, stock, msg = self.validate_outbound_quantity(vaccine_id, quantity)
            if not valid:
                return (False, msg, None)

            type_valid, type_msg = self.validate_outbound_by_type(outbound_type, outbound_data)
            if not type_valid:
                return (False, type_msg, None)

            recipient_unit = self.get_recipient_unit_by_id(recipient_unit_id)
            recipient_name = recipient_unit.get('name', '未知单位') if recipient_unit else '未知单位'

            outbound_id = self.generate_outbound_id()
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            record = {
                'outbound_id': outbound_id,
                'vaccine_id': vaccine.get('id'),
                'vaccine_name': vaccine.get('name'),
                'batch_number': vaccine.get('batch_number'),
                'recipient_unit_id': recipient_unit_id,
                'recipient_unit_name': recipient_name,
                'outbound_type': outbound_type,
                'quantity': quantity,
                'available_stock_before': stock,
                'transport_method': outbound_data.get('transport_method', ''),
                'departure_temp': str(outbound_data.get('departure_temp', '')),
                'reviewer': outbound_data.get('reviewer', ''),
                'operator': outbound_data.get('operator', 'system'),
                'outbound_time': now,
                'uploaded_to_national': outbound_data.get('uploaded_to_national', False),
                'status': 'completed',
                'remark': outbound_data.get('remark', ''),
                'related_order_id': outbound_data.get('related_order_id'),
                'create_time': now,
                'review_time': now if outbound_data.get('reviewer') else None,
                'complete_time': now,
                'vaccine_expiry_date': vaccine.get('expiry_date'),
                'manufacturer': vaccine.get('manufacturer', '')
            }

            previous_quantity = vaccine.get('quantity', 0)
            previous_status = vaccine.get('status')
            self.outbound_records.append(record)
            vaccine['quantity'] = stock - quantity
            if vaccine['quantity'] == 0:
                vaccine['status'] = 'out_stock'

            if not self.save_data():
                self.outbound_records.pop()
                vaccine['quantity'] = previous_quantity
                vaccine['status'] = previous_status
                return (False, '❌ 出库记录保存失败', None)

            type_display = {
                'allocation': '调拨',
                'vaccination': '接种',
                'scrap': '报废',
                'return': '退回'
            }.get(outbound_type, outbound_type)

            self.log_operation(
                f'出库登记: {vaccine.get("name")} {quantity}支 → {recipient_name} ({type_display}) 单号:{outbound_id}'
            )

            return (True, f'✅ 出库成功！单号: {outbound_id}', record)

        except Exception as e:
            return (False, f'❌ 出库失败: {str(e)}', None)

    def get_outbound_records(self, filters=None):
        records = list(self.outbound_records)

        if not filters:
            records.sort(key=lambda x: x.get('create_time', ''), reverse=True)
            return records

        if filters.get('vaccine_name'):
            records = [r for r in records if filters['vaccine_name'] in r.get('vaccine_name', '')]

        if filters.get('batch_number'):
            records = [r for r in records if filters['batch_number'] in r.get('batch_number', '')]

        if filters.get('start_date'):
            records = [r for r in records if r.get('outbound_time', '')[:10] >= filters['start_date']]
        if filters.get('end_date'):
            records = [r for r in records if r.get('outbound_time', '')[:10] <= filters['end_date']]

        if filters.get('outbound_type'):
            records = [r for r in records if r.get('outbound_type') == filters['outbound_type']]

        if filters.get('recipient_unit_name'):
            records = [r for r in records if filters['recipient_unit_name'] in r.get('recipient_unit_name', '')]

        if filters.get('status'):
            records = [r for r in records if r.get('status') == filters['status']]

        records.sort(key=lambda x: x.get('create_time', ''), reverse=True)
        return records

    def get_outbound_record_by_id(self, outbound_id):
        for r in self.outbound_records:
            if r.get('outbound_id') == outbound_id:
                return r
        return None

    def get_outbound_statistics(self):
        total = len(self.outbound_records)
        total_quantity = sum(r.get('quantity', 0) for r in self.outbound_records)

        type_stats = {}
        for t in ['allocation', 'vaccination', 'scrap', 'return']:
            type_records = [r for r in self.outbound_records if r.get('outbound_type') == t]
            type_stats[t] = {
                'count': len(type_records),
                'quantity': sum(r.get('quantity', 0) for r in type_records)
            }

        today = datetime.datetime.now().strftime('%Y-%m-%d')
        today_records = [r for r in self.outbound_records if r.get('outbound_time', '').startswith(today)]

        return {
            'total_records': total,
            'total_quantity': total_quantity,
            'today_count': len(today_records),
            'today_quantity': sum(r.get('quantity', 0) for r in today_records),
            'by_type': type_stats
        }



    # ==================== 统计报表 ====================

    def get_dashboard_stats(self):
        today = datetime.date.today()

        stock_vaccines = [v for v in self.vaccines if v.get('status') == 'in_stock']

        total_quantity = sum(v.get('quantity', 0) for v in stock_vaccines)

        warning_varieties = set()
        for v in stock_vaccines:
            if v.get('quantity', 0) < 10:
                warning_varieties.add(v['name'])
            else:
                try:
                    expiry = datetime.date.fromisoformat(v['expiry_date'])
                    if (expiry - today).days <= 30:
                        warning_varieties.add(v['name'])
                except (ValueError, TypeError):
                    pass

        expired_varieties = set()
        for v in stock_vaccines:
            try:
                expiry = datetime.date.fromisoformat(v['expiry_date'])
                if (expiry - today).days < 0:
                    expired_varieties.add(v['name'])
            except (ValueError, TypeError):
                pass

        total_capacity = sum(s.get('capacity', 0) for s in self.cold_storages)
        total_used = sum(s.get('used', 0) for s in self.cold_storages)
        avg_storage_usage = round((total_used / total_capacity * 100), 1) if total_capacity > 0 else 0.0

        kpi = {
            'total_quantity': total_quantity,
            'warning_varieties': len(warning_varieties),
            'expired_varieties': len(expired_varieties),
            'avg_storage_usage': avg_storage_usage
        }

        category_data = {}
        for v in stock_vaccines:
            cat = v.get('category', '未分类')
            if cat not in category_data:
                category_data[cat] = {'quantity': 0, 'varieties': set()}
            category_data[cat]['quantity'] += v.get('quantity', 0)
            category_data[cat]['varieties'].add(v['name'])

        category_distribution = []
        for cat, data in category_data.items():
            category_distribution.append({
                'category': cat,
                'quantity': data['quantity'],
                'percentage': round(data['quantity'] / total_quantity * 100, 1) if total_quantity > 0 else 0,
                'variety_count': len(data['varieties'])
            })
        category_distribution.sort(key=lambda x: x['quantity'], reverse=True)

        manufacturer_data = {}
        for v in stock_vaccines:
            mf = v.get('manufacturer', '未知厂家')
            if mf not in manufacturer_data:
                manufacturer_data[mf] = {'quantity': 0, 'varieties': set()}
            manufacturer_data[mf]['quantity'] += v.get('quantity', 0)
            manufacturer_data[mf]['varieties'].add(v['name'])

        manufacturer_distribution = []
        for mf, data in manufacturer_data.items():
            manufacturer_distribution.append({
                'manufacturer': mf,
                'quantity': data['quantity'],
                'percentage': round(data['quantity'] / total_quantity * 100, 1) if total_quantity > 0 else 0,
                'variety_count': len(data['varieties'])
            })
        manufacturer_distribution.sort(key=lambda x: x['quantity'], reverse=True)

        storage_distribution = []
        for s in self.cold_storages:
            storage_vaccines = [v for v in stock_vaccines if str(v.get('storage_id')) == str(s.get('id'))]
            used_qty = sum(v.get('quantity', 0) for v in storage_vaccines)
            capacity = s.get('capacity', 0)
            usage_rate = round(used_qty / capacity * 100, 1) if capacity > 0 else 0

            storage_distribution.append({
                'storage_id': s.get('id'),
                'name': s.get('name', ''),
                'type': s.get('type', ''),
                'capacity': capacity,
                'used': used_qty,
                'usage_rate': usage_rate,
                'variety_count': len(set(v['name'] for v in storage_vaccines))
            })
        storage_distribution.sort(key=lambda x: x['usage_rate'], reverse=True)

        return {
            'kpi': kpi,
            'category_distribution': category_distribution,
            'manufacturer_distribution': manufacturer_distribution,
            'storage_distribution': storage_distribution
        }

    def get_expiry_tier_stats(self):
        today = datetime.date.today()
        stock_vaccines = [v for v in self.vaccines if v.get('status') == 'in_stock']

        tiers = {
            'expired': {'varieties': 0, 'quantity': 0, 'items': []},
            'warning': {'varieties': set(), 'quantity': 0, 'items': []},
            'safe': {'varieties': set(), 'quantity': 0, 'items': []}
        }
        details = []

        for v in stock_vaccines:
            try:
                expiry = datetime.date.fromisoformat(v['expiry_date'])
                days_remaining = (expiry - today).days
                total_days = (expiry - datetime.date.fromisoformat(v['production_date'])).days if v.get('production_date') else days_remaining
                remaining_ratio = round(days_remaining / total_days * 100, 1) if total_days > 0 else 0

                storage_name = ''
                for s in self.cold_storages:
                    if str(s.get('id')) == str(v.get('storage_id')):
                        storage_name = s.get('name', '')
                        break

                if days_remaining < 0:
                    tier = 'expired'
                    tiers['expired']['varieties'] += 1
                    tiers['expired']['items'].append(v)
                elif days_remaining <= 30:
                    tier = 'warning'
                    tiers['warning']['varieties'].add(v['name'])
                    tiers['warning']['items'].append(v)
                else:
                    tier = 'safe'
                    tiers['safe']['varieties'].add(v['name'])
                    tiers['safe']['items'].append(v)

                tiers[tier]['quantity'] += v.get('quantity', 0)

                details.append({
                    'name': v.get('name'),
                    'batch_number': v.get('batch_number', ''),
                    'expiry_date': v.get('expiry_date'),
                    'days_remaining': days_remaining,
                    'total_days': total_days,
                    'remaining_ratio': remaining_ratio,
                    'quantity': v.get('quantity', 0),
                    'storage_name': storage_name,
                    'tier': tier
                })

            except (ValueError, TypeError):
                tiers['safe']['quantity'] += v.get('quantity', 0)
                tiers['safe']['varieties'].add(v.get('name', ''))

        tiers['warning']['varieties'] = len(tiers['warning']['varieties'])
        tiers['safe']['varieties'] = len(tiers['safe']['varieties'])

        details.sort(key=lambda x: x['days_remaining'])

        return {
            'tiers': tiers,
            'details': details
        }

    def get_abc_classification(self):
        stock_vaccines = [v for v in self.vaccines if v.get('status') == 'in_stock']

        variety_quantities = {}
        for v in stock_vaccines:
            name = v.get('name')
            variety_quantities[name] = variety_quantities.get(name, 0) + v.get('quantity', 0)

        sorted_varieties = sorted(variety_quantities.items(), key=lambda x: x[1], reverse=True)

        total_quantity = sum(qty for _, qty in sorted_varieties)

        class_A = {'count': 0, 'quantity': 0, 'ratio': 0}
        class_B = {'count': 0, 'quantity': 0, 'ratio': 0}
        class_C = {'count': 0, 'quantity': 0, 'ratio': 0}

        cumulative = 0
        details = []

        for name, quantity in sorted_varieties:
            percentage = round(quantity / total_quantity * 100, 1) if total_quantity > 0 else 0
            cumulative += percentage

            if cumulative <= 80:
                abc_class = 'A'
                class_A['count'] += 1
                class_A['quantity'] += quantity
            elif cumulative <= 95:
                abc_class = 'B'
                class_B['count'] += 1
                class_B['quantity'] += quantity
            else:
                abc_class = 'C'
                class_C['count'] += 1
                class_C['quantity'] += quantity

            details.append({
                'name': name,
                'quantity': quantity,
                'percentage': percentage,
                'cumulative': round(cumulative, 1),
                'abc_class': abc_class
            })

        class_A['ratio'] = round(class_A['quantity'] / total_quantity * 100, 1) if total_quantity > 0 else 0
        class_B['ratio'] = round(class_B['quantity'] / total_quantity * 100, 1) if total_quantity > 0 else 0
        class_C['ratio'] = round(class_C['quantity'] / total_quantity * 100, 1) if total_quantity > 0 else 0

        return {
            'summary': {
                'total_varieties': len(sorted_varieties),
                'class_A': class_A,
                'class_B': class_B,
                'class_C': class_C
            },
            'details': details
        }

    def get_fefo_compliance_rate(self):
        if not self.outbound_records:
            return {
                'compliance_rate': None,
                'total_records': 0,
                'compliant_count': 0,
                'non_compliant_details': [],
                'is_simulation': True
            }

        compliant_count = 0
        non_compliant = []

        for record in self.outbound_records:
            vaccine_id = record.get('vaccine_id')
            outbound_batch = record.get('batch_number', '')

            batches = self.get_fifo_vaccines_by_id(vaccine_id)
            if not batches or len(batches) < 2:
                compliant_count += 1
                continue

            earliest_expiry_batch = min(batches, key=lambda x: x.get('expiry_date', '9999-12-31'))

            if outbound_batch == earliest_expiry_batch.get('batch_number'):
                compliant_count += 1
            else:
                non_compliant.append({
                    'outbound_id': record.get('outbound_id'),
                    'vaccine_name': record.get('vaccine_name'),
                    'outbound_batch': outbound_batch,
                    'should_be_batch': earliest_expiry_batch.get('batch_number'),
                    'earliest_expiry': earliest_expiry_batch.get('expiry_date'),
                    'outbound_time': record.get('outbound_time')
                })

        total = len(self.outbound_records)
        rate = round(compliant_count / total * 100, 1) if total > 0 else 0

        return {
            'compliance_rate': rate,
            'total_records': total,
            'compliant_count': compliant_count,
            'non_compliant_details': non_compliant,
            'is_simulation': False
        }

    def get_fifo_vaccines_by_id(self, vaccine_id):
        batches = []
        for v in self.vaccines:
            if (str(v.get('id')) == str(vaccine_id) and
                v.get('status') == 'in_stock' and
                v.get('quantity', 0) > 0):
                batches.append(v)
        batches.sort(key=lambda x: x.get('expiry_date', '9999-12-31'))
        return batches

    def get_inventory_flow_summary(self, start_date=None, end_date=None):
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')

        all_stock = {}

        for v in self.vaccines:
            name = v.get('name')
            category = v.get('category', '')

            if name not in all_stock:
                all_stock[name] = {
                    'name': name,
                    'category': category,
                    'opening_stock': 0,
                    'inbound_quantity': 0,
                    'outbound_quantity': 0
                }

        for v in self.vaccines:
            name = v.get('name')
            category = v.get('category', '')
            in_time = v.get('入库时间', '') or v.get('stock_time', '')

            if name not in all_stock:
                all_stock[name] = {
                    'name': name,
                    'category': category,
                    'opening_stock': 0,
                    'inbound_quantity': 0,
                    'outbound_quantity': 0
                }

            if in_time:
                try:
                    in_date = in_time.split(' ')[0]
                    if start_date and in_date >= start_date and in_date <= end_date:
                        all_stock[name]['inbound_quantity'] += v.get('quantity', 0)
                    elif not start_date or in_date < start_date:
                        if v.get('status') == 'in_stock':
                            all_stock[name]['opening_stock'] += v.get('quantity', 0)
                except (IndexError, ValueError):
                    pass

        for record in self.outbound_records:
            out_time = record.get('outbound_time', '')
            name = record.get('vaccine_name', '')

            if name not in all_stock:
                all_stock[name] = {
                    'name': name,
                    'category': '',
                    'opening_stock': 0,
                    'inbound_quantity': 0,
                    'outbound_quantity': 0
                }

            if out_time:
                try:
                    out_date = out_time.split(' ')[0]
                    if start_date and out_date >= start_date and out_date <= end_date:
                        all_stock[name]['outbound_quantity'] += record.get('quantity', 0)
                except (IndexError, ValueError):
                    pass

        summary = []
        for name, data in all_stock.items():
            closing_stock = data['opening_stock'] + data['inbound_quantity'] - data['outbound_quantity']

            if data['opening_stock'] > 0:
                change_rate = round((closing_stock - data['opening_stock']) / data['opening_stock'] * 100, 1)
            else:
                change_rate = 100.0 if data['inbound_quantity'] > 0 else 0.0

            summary.append({
                'name': name,
                'category': data['category'],
                'opening_stock': data['opening_stock'],
                'inbound_quantity': data['inbound_quantity'],
                'outbound_quantity': data['outbound_quantity'],
                'closing_stock': closing_stock,
                'change_rate': change_rate
            })

        summary.sort(key=lambda x: abs(x['change_rate']), reverse=True)

        return {
            'period': {'start': start_date or '-', 'end': end_date},
            'summary': summary
        }

    def get_outbound_type_breakdown(self, start_date=None, end_date=None):
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')

        type_names = {
            'allocation': '调拨',
            'vaccination': '接种',
            'scrap': '报废',
            'return': '退回'
        }

        type_stats = {t: {'count': 0, 'quantity': 0} for t in type_names.keys()}

        for record in self.outbound_records:
            out_time = record.get('outbound_time', '')
            otype = record.get('outbound_type', '')

            if out_time and otype in type_stats:
                try:
                    out_date = out_time.split(' ')[0]
                    if start_date and out_date >= start_date and out_date <= end_date:
                        type_stats[otype]['count'] += 1
                        type_stats[otype]['quantity'] += record.get('quantity', 0)
                except (IndexError, ValueError):
                    pass
            elif not start_date and otype in type_stats:
                type_stats[otype]['count'] += 1
                type_stats[otype]['quantity'] += record.get('quantity', 0)

        total_count = sum(t['count'] for t in type_stats.values())
        total_quantity = sum(t['quantity'] for t in type_stats.values())

        types = []
        for t, stats in type_stats.items():
            types.append({
                'type': t,
                'type_name': type_names[t],
                'count': stats['count'],
                'quantity': stats['quantity'],
                'percentage': round(stats['quantity'] / total_quantity * 100, 1) if total_quantity > 0 else 0
            })
        types.sort(key=lambda x: x['quantity'], reverse=True)

        return {
            'period': {'start': start_date or '-', 'end': end_date},
            'types': types,
            'total_count': total_count,
            'total_quantity': total_quantity
        }

    def get_merged_flow_timeline(self, start_date=None, end_date=None, limit=100):
        records = []

        for v in self.vaccines:
            in_time = v.get('入库时间', '') or v.get('stock_time', '')
            if in_time:
                try:
                    in_date = in_time.split(' ')[0]
                    if start_date and (in_date < start_date or in_date > end_date):
                        continue
                    records.append({
                        'time': in_time,
                        'flow_type': 'inbound',
                        'name': v.get('name'),
                        'batch_number': v.get('batch_number', ''),
                        'quantity': v.get('quantity', 0),
                        'business_type': '入库',
                        'operator': v.get('operator', 'system')
                    })
                except (IndexError, ValueError):
                    continue

        for record in self.outbound_records:
            out_time = record.get('outbound_time', '')
            if out_time:
                try:
                    out_date = out_time.split(' ')[0]
                    if start_date and (out_date < start_date or out_date > end_date):
                        continue

                    type_names = {
                        'allocation': '调拨',
                        'vaccination': '接种',
                        'scrap': '报废',
                        'return': '退回'
                    }

                    records.append({
                        'time': out_time,
                        'flow_type': 'outbound',
                        'name': record.get('vaccine_name'),
                        'batch_number': record.get('batch_number', ''),
                        'quantity': -record.get('quantity', 0),
                        'business_type': type_names.get(record.get('outbound_type', ''), record.get('outbound_type', '')),
                        'operator': record.get('operator', '')
                    })
                except (IndexError, ValueError):
                    continue

        records.sort(key=lambda x: x['time'], reverse=True)

        has_more = len(records) > limit

        return {
            'records': records[:limit],
            'total_count': len(records),
            'has_more': has_more
        }

    def get_inventory_forecast(self, days=30):
        today = datetime.date.today()

        outbound_by_day = {}
        for record in self.outbound_records:
            out_time = record.get('outbound_time', '')
            if out_time:
                try:
                    out_date = out_time.split(' ')[0]
                    if out_date not in outbound_by_day:
                        outbound_by_day[out_date] = 0
                    outbound_by_day[out_date] += record.get('quantity', 0)
                except (IndexError, ValueError):
                    continue

        if not outbound_by_day:
            current_stock = sum(v.get('quantity', 0) for v in self.vaccines
                             if v.get('status') == 'in_stock')

            return {
                'forecast_days': days,
                'daily_avg_consumption': 0,
                'current_stock': current_stock,
                'forecast_table': [],
                'indicators': {
                    'avg_daily_consumption': 0,
                    'estimated_stockout_date': None,
                    'inventory_turnover_days': None
                },
                'is_simulation': True
            }

        sorted_dates = sorted(outbound_by_day.keys())
        total_consumption = sum(outbound_by_day.values())
        avg_daily = total_consumption / max(len(sorted_dates), 1)

        current_stock = sum(v.get('quantity', 0) for v in self.vaccines
                         if v.get('status') == 'in_stock')

        forecast_table = []
        prev_stock = current_stock
        for i in range(1, days + 1):
            future_date = today + datetime.timedelta(days=i)
            daily_change = -avg_daily
            predicted = max(0, prev_stock + daily_change)

            if predicted == prev_stock:
                trend = '→平稳'
            elif daily_change < 0:
                trend = '↓下降'
            else:
                trend = '↑上升'

            forecast_table.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'predicted_stock': round(predicted, 1),
                'daily_change': round(daily_change, 1),
                'trend': trend
            })

            prev_stock = predicted

        indicators = {
            'avg_daily_consumption': round(avg_daily, 1),
            'estimated_stockout_date': None,
            'inventory_turnover_days': round(current_stock / avg_daily, 1) if avg_daily > 0 else None
        }

        if avg_daily > 0 and current_stock > 0:
            days_to_zero = int(current_stock / avg_daily)
            stockout_date = today + datetime.timedelta(days=days_to_zero)
            indicators['estimated_stockout_date'] = stockout_date.strftime('%Y-%m-%d')

        return {
            'forecast_days': days,
            'daily_avg_consumption': round(avg_daily, 1),
            'current_stock': current_stock,
            'forecast_table': forecast_table,
            'indicators': indicators,
            'is_simulation': False
        }


vaccine_service = VaccineService()
