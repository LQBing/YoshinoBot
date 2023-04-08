import asyncio
from typing import Any, Dict
from aiocqhttp.api import Api

from .components.web_operation import register_routes
from .components.kernel import init, execute, jobs, match
from .components.score import score_table
from .components.realize import *
from .components.realize import (_level_by_cycle, _get_nickname_by_qqid,
				_get_group_previous_challenge, _update_group_list_async, 
				_fetch_member_list_async, _update_all_group_members_async,
				_update_user_nickname_async, _boss_data_dict, _get_available_empty_battle_id,
				_update_user_profile_image)


class ClanBattle:
	Passive = True
	Active = True
	Request = True

	#### 核心
	init = init			#初始化
	execute = execute	#执行
	jobs = jobs			#验证
	match = match		#匹配
	#### 核心

	#构造函数/初始化
	def __init__(self, glo_setting:Dict[str, Any], bot_api:Api, boss_id_name:Dict, *args, **kwargs):
		# data initialize
		self._boss_status:Dict[str, asyncio.Future] = {}
		self.init(glo_setting, bot_api, boss_id_name, args, kwargs)
		
	
	register_routes = register_routes #网页端操作

	score_table = score_table	#业绩
	text_2_pic = text_2_pic		#文字转图片

	_level_by_cycle = _level_by_cycle									##等级周目
	_get_nickname_by_qqid = _get_nickname_by_qqid						##通过qq号获取成员名字
	_get_group_previous_challenge = _get_group_previous_challenge		##获取上一个出刀记录
	_update_group_list_async = _update_group_list_async					##更新群列表
	_fetch_member_list_async = _fetch_member_list_async					##获取群成员列表
	_update_all_group_members_async = _update_all_group_members_async	##更新所有群成员
	_update_user_nickname_async = _update_user_nickname_async			##更新成员名字
	_boss_data_dict = _boss_data_dict									##获取boss当前数据
	_get_available_empty_battle_id = _get_available_empty_battle_id		##获取公会最靠前的空白档案号
	_update_user_profile_image = _update_user_profile_image             ##刷新用户头像

	create_group = create_group								##创建公会
	bind_group = bind_group									##加入公会
	drop_member = drop_member								##删除成员
	boss_status_summary = boss_status_summary				##当前的boss状态
	challenge = challenge									##报刀
	undo = undo												##撤销上一刀的伤害/删除上一刀的记录
	modify = modify											##修改boss状态
	change_game_server = change_game_server					##修改服务器
	get_data_slot_record_count = get_data_slot_record_count	##获取当期会战数据记录档案的编号
	clear_data_slot = clear_data_slot						##清空会战数据记录档案
	switch_data_slot = switch_data_slot						##切换会战数据记录档案
	send_private_remind = send_private_remind				##向个人私聊发送出刀提醒
	behelf_remind = behelf_remind							##代刀提醒
	send_remind = send_remind								##发送出刀提醒

	apply_for_challenge = apply_for_challenge				##申请出刀
	cancel_blade = cancel_blade								##取消申请出刀
	save_slot = save_slot									##SL
	report_hurt = report_hurt								##报伤害/记录伤害
	challenger_info = challenger_info						##当前出刀信息
	challenger_info_small = challenger_info_small			##单个boss出刀信息
	check_blade = check_blade								##检查是否已申请出刀
	put_on_the_tree = put_on_the_tree						##挂树
	take_it_of_the_tree = take_it_of_the_tree				##下树
	get_in_boss_num = get_in_boss_num						##获取boss_num
	subscribe = subscribe									##预约
	subscribe_cancel = subscribe_cancel						##取消预约
	get_subscribe_list = get_subscribe_list					##获取预约列表
	challenge_record = challenge_record						##出刀记录

	get_report = get_report										##获取报告
	get_battle_member_list = get_battle_member_list				##从会战记录里获取成员列表
	get_member_list = get_member_list							##获取所有成员列表
	
	query_tree = query_tree
