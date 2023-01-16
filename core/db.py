# -*- coding: utf-8 -*-

import mysql.connector

HOST = u''
PASSWORD = u''


def get_con_data_info(db='data_info'):

    conn = None

    if conn is None:
        conn = mysql.connector.connect(
            host=HOST,
            user='root',
            password=PASSWORD,
            db=db,
            charset='utf8'
        )
    return conn


def get_con_smart_maker(db='smart_maker'):

    conn = None

    if conn is None:
        conn = mysql.connector.connect(
            host=HOST,
            user='root',
            password=PASSWORD,
            db=db,
            charset='utf8'
        )
    return conn


def get_log_info(cstatus, drive, line_edit, path_or_file):
    table = cstatus + drive
    conn = get_con_data_info()
    curs = conn.cursor()
    line_edit = line_edit.replace('\\', '\\\\')

    data = None
    if path_or_file == 0:
        data = 'path'
    if path_or_file == 1:
        data = 'file'

    # 라이트 조인
    # sql = "SELECT " \
    #       "i.date_time, i.path, i.`file`, i.access_mask, u.nickname, i.user_ip " \
    #       "FROM " \
    #       "users u " \
    #       "RIGHT OUTER JOIN " \
    #       "{} i " \
    #       "ON " \
    #       "u.ip = i.user_ip " \
    #       "WHERE " \
    #       "path LIKE %s OR file LIKE %s ".format(drive_name)

    # 레프트 조인
    # sql = "SELECT " \
    #       "i.date_time, i.path, i.`file`, i.access_mask, u.nickname, i.user_ip " \
    #       "FROM " \
    #       "{} i " \
    #       "LEFT OUTER JOIN " \
    #       "users u " \
    #       "ON " \
    #       "i.user_ip = u.ip  " \
    #       "WHERE " \
    #       "{} LIKE %s".format(table, data)

    sql = "SELECT " \
          "date_time, path, file, access_mask, user_ip " \
          "FROM " \
          "{} " \
          "WHERE " \
          "{} LIKE %s".format(table, data)

    curs.execute(sql, (line_edit,))

    res = curs.fetchall()
    conn.close()
    if res:
        # set 함수를 사용하여 중복된 데이터는 제외
        res = set(res)
        res = list(res)
        res = [list(res[x]) for x in range(len(res))]
        return res


def get_name_from_ip(ip):
    """아이피 정보가 매치되는 유저의 이름을 가져온다."""
    conn = get_con_smart_maker()
    curs = conn.cursor()
    sql = 'SELECT name FROM users WHERE ip LIKE %s'
    curs.execute(sql, (ip,))

    res = curs.fetchall()
    conn.close()
    if res:
        res = [list(res[x]) for x in range(len(res))]
        res = res[0][0]
        res = str(res)

        return res


def update_user_information(filed, modified_data, id):
    """
    user 테이블 위젯에서 변경한 필드값을 데이터 베이스에 업데이트 한다.
    """
    conn = get_con_smart_maker()
    curs = conn.cursor()
    curs.execute(
        'UPDATE users '
        'SET '
        '{} = %s '
        'WHERE '
        'id = %s '.format(filed),
        (modified_data, id,),
    )
    conn.commit()
    conn.close()


def save_selected_netdrive(selected_ids, user_id):
    """
    connections 테이블에 user_id(user 테이블의 id),
    netdrive_id(netdrive테이블의 id) 데이터를 저장한다.
    """
    conn = get_con_smart_maker()
    curs = conn.cursor()

    curs.execute(
        'DELETE FROM connections '
        'WHERE users_id=%s',
        (user_id,),
    )

    for nid in selected_ids:
        curs.execute(
            'insert into connections (users_id, netdrive_id) '
            'values (%s, %s)',
            (user_id, nid),
        )

    conn.commit()
    conn.close()


def get_user_info(input_search):
    """팀명이나 이름으로 검색결과를 보여준다."""
    conn = get_con_smart_maker()
    curs = conn.cursor()
    curs.execute(
        'SELECT '
        '   u.id, '
        '   u.team, '
        '   u.nickname, '
        '   u.name, '
        '   u.login_id, '
        '   u.email_address, '
        '   u.ip '
        'FROM users u '
        'WHERE '
        '   u.team LIKE %s OR u.name LIKE %s',
        ("%" + input_search + "%", "%" + input_search + "%",)
    )

    result = curs.fetchall()
    conn.close()

    if result is not None:
        return result
    else:
        return


def get_all_user_info():
    """전체 유저 리스트를 보여준다."""
    conn = get_con_smart_maker()
    curs = conn.cursor()

    curs.execute(
        'SELECT '
        '   id, '
        '   team, '
        '   nickname, '
        '   name, '
        '   login_id, '
        '   email_address, '
        '   ip '
        'FROM users'
    )

    result = curs.fetchall()
    conn.close()

    if result is not None:
        return result
    else:
        return


def get_drive_list(user_id):
    """사용중인 네트워크 드라이브 리스트를 보여준다."""
    conn = get_con_smart_maker()
    curs = conn.cursor()
    curs.execute(
        'SELECT '
        '   n.drive, '
        '   s.hostname, '
        '   s.private_ip, '
        '   n.description, '
        '   c.netdrive_id  '
        'FROM connections c '
        'LEFT JOIN netdrive n ON n.id=c.netdrive_id '
        'LEFT JOIN users u ON u.id=c.users_id '
        'LEFT JOIN server s ON s.id=n.server_id '
        'WHERE '
        ' c.users_id LIKE %s',
        (user_id,)
    )
    result = curs.fetchall()
    conn.close()

    if result is not None:
        return result
    else:
        return


def add_new_user(team, nickname, name, login_id, email_address, ip, auth_id):
    """신규 사용자를 추가한다."""
    conn = get_con_smart_maker()
    curs = conn.cursor()

    sql = 'INSERT INTO ' \
          'users (team, nickname, name, login_id, email_address, ip, auth_id) ' \
          'VALUES ' \
          "('{}', '{}', '{}', '{}', '{}', '{}', '{}')" \
          ''.format(team, nickname, name, login_id, email_address, ip, auth_id)
    curs.execute(sql)
    conn.commit()

    conn.close()


def delete_user(users_id):
    """사용자를 삭제한다."""
    conn = get_con_smart_maker()
    curs = conn.cursor()

    curs.execute(
      'DELETE FROM connections '
      'WHERE users_id=%s',
      (users_id,),
    )

    progress = 1

    if progress == 1:
        sql = 'DELETE FROM ' \
              'users ' \
              'WHERE ' \
              "id='{} '" \
              ''.format(users_id)

        curs.execute(sql)
    conn.commit()
    conn.close()