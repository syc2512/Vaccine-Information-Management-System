import datetime
import re


def validate_date_format(date_str):
    if not date_str or not str(date_str).strip():
        return (False, '日期不能为空')

    date_str = str(date_str).strip()

    try:
        parsed = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return (True, parsed.strftime('%Y-%m-%d'))
    except ValueError:
        pass

    try:
        parsed = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return (True, parsed.strftime('%Y-%m-%d %H:%M:%S'))
    except ValueError:
        pass

    for fmt in ['%Y/%m/%d', '%Y-%m-%dT%H:%M:%S', '%Y%m%d']:
        try:
            parsed = datetime.datetime.strptime(date_str, fmt)
            return (True, parsed.strftime('%Y-%m-%d'))
        except ValueError:
            continue

    return (False, f'日期格式不正确: {date_str}，请使用 YYYY-MM-DD 格式')


def validate_vaccine_data(data):
    errors = []

    name = str(data.get('name', '')).strip()
    if not name:
        errors.append('疫苗名称不能为空')

    category = str(data.get('category', '')).strip()
    if not category:
        errors.append('疫苗类别不能为空')
    elif category.isdigit():
        errors.append(f'类别名称不能为纯数字: "{category}"')

    manufacturer = str(data.get('manufacturer', '')).strip()
    if not manufacturer:
        errors.append('生产厂家不能为空')

    batch_number = str(data.get('batch_number', '')).strip()
    if not batch_number:
        errors.append('批号不能为空')
    elif not re.match(r'^[A-Za-z0-9\-_]+$', batch_number):
        errors.append(f'批号格式不正确: "{batch_number}"，只允许字母、数字、横线、下划线')

    production_date = str(data.get('production_date', '')).strip()
    expiry_date = str(data.get('expiry_date', '')).strip()

    prod_valid, prod_result = validate_date_format(production_date) if production_date else (False, '')
    if not production_date:
        errors.append('生产日期不能为空')
    elif not prod_valid:
        errors.append(f'生产日期格式错误: {prod_result}')

    expiry_valid, expiry_result = validate_date_format(expiry_date) if expiry_date else (False, '')
    if not expiry_date:
        errors.append('有效期不能为空')
    elif not expiry_valid:
        errors.append(f'有效期格式错误: {expiry_result}')

    if prod_valid and expiry_valid:
        try:
            prod_dt = datetime.datetime.strptime(production_date, '%Y-%m-%d').date()
            expiry_dt = datetime.datetime.strptime(expiry_date, '%Y-%m-%d').date()
            if expiry_dt <= prod_dt:
                errors.append(f'有效期({expiry_date})必须晚于生产日期({production_date})')
            if expiry_dt <= datetime.date.today():
                errors.append(f'警告：有效期({expiry_date})已过期或今天到期')
        except ValueError:
            pass

    try:
        quantity = int(data.get('quantity', 0))
        if quantity <= 0:
            errors.append(f'数量必须大于0，当前值: {quantity}')
    except (ValueError, TypeError):
        errors.append(f'数量必须为有效整数，当前值: {data.get("quantity")}')

    if errors:
        return (False, '\n'.join(f'• {e}' for e in errors))

    return (True, '校验通过')


def validate_category_data(data, existing_categories):
    name = str(data.get('name', '')).strip()

    if not name:
        return (False, '类别名称不能为空')

    if name.isdigit():
        return (False, f'类别名称不能为纯数字: "{name}"')

    if len(name) > 50:
        return (False, '类别名称不能超过50个字符')

    current_id = data.get('id')
    for cat in existing_categories:
        cat_name = str(cat.get('name', '')).strip()
        cat_id = cat.get('id')
        if cat_name == name and cat_id != current_id:
            return (False, f'类别名称 "{name}" 已存在（ID: {cat_id}），请使用其他名称')

    return (True, '校验通过')
