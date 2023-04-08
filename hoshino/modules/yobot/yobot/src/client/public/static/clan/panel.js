if (!Object.defineProperty) {
    alert('浏览器版本过低');
}
var vm = new Vue({
    el: '#app',
    data: {
        activeIndex: "1",
        groupData: {},
        bossData: { 1:{is_next:false,cycle:0,health:0,full_health:0,icon_id:0,challenger:{}},
                    2:{is_next:false,cycle:0,health:0,full_health:0,icon_id:0,challenger:{}},
                    3:{is_next:false,cycle:0,health:0,full_health:0,icon_id:0,challenger:{}},
                    4:{is_next:false,cycle:0,health:0,full_health:0,icon_id:0,challenger:{}},
                    5:{is_next:false,cycle:0,health:0,full_health:0,icon_id:0,challenger:{}}},
        is_admin: false,
        self_id: 0,
        members: [],

        isMobile: false,    //是否是手机
        boxShow:{1:false,2:false,3:false,4:false,5:false},  //手机版面板抽屉显示

        base_cycle: 1,  //当前基础周目

        //代x
        behalf: null,               //报刀
        behalf_apply: null,         //申请出刀
        behalf_cancelApply: null,   //取消申请出刀
        behalf_tree: null,          //挂树
        behalf_cancelTree: null,    //取消挂树

        applyDialog: {1:false,2:false,3:false,4:false,5:false},         //申请出刀弹窗是否显示
        cancelApplyDialog: {1:false,2:false,3:false,4:false,5:false},   //取消出刀弹窗是否显示
        is_continue:false,          //申请出刀弹窗内 是否是补偿刀 开关

        recordDamageDialog: {1:false,2:false,3:false,4:false,5:false},  //报刀弹窗是否显示
        defeat: null,       //报刀弹窗内 是否击败boss 开关
        damage: 0,          //报刀弹窗内 伤害值

        treeDialog: false,          //挂树弹窗是否显示
        cancelTreeDialog: false,    //取消挂树弹窗是否显示
        treeNum:1,                  //挂树弹窗选择的boss

        statusFormVisible: false,   //修改boss状态弹窗是否显示
        boss_num: 1,                //选择操作修改boss状态的boss编号

        slDialog:false,         //sl弹窗是否显示
        cancelSlDialog:false,   //取消sl弹窗是否显示
        slMember:0,             //需要记录sl的成员

        subscribe: null,        //预约/取消预约 哪个boss
        message: '',            //预约留言（心理安慰，无实际作用）
        subscribeFormVisible: false,    //添加预约弹窗是否显示
        subscribeCancelVisible: false,  //取消预约弹窗是否显示
        leavePage: false,
        challengersList: {1:false,2:false,3:false,4:false,5:false},     //各个正在挑战的玩家列表显示
    },
    mounted() {
        var thisvue = this;
        axios.post("./api/", {
            action: 'get_data',
            csrf_token: csrf_token,
        }).then(function (res) {
            if (res.data.code == 0) {
                thisvue.groupData = res.data.groupData;
                thisvue.bossData = res.data.bossData;
                thisvue.base_cycle = res.data.groupData.cycle;
                thisvue.is_admin = res.data.selfData.is_admin;
                thisvue.self_id = res.data.selfData.user_id;
                thisvue.boss_num = 1;
                document.title = res.data.groupData.group_name + ' - 公会战';
            } else {
                thisvue.$alert(res.data.message, '加载数据错误');
            }
        }).catch(function (error) {
            thisvue.$alert(error, '加载数据错误');
        });
        axios.post("./api/", {
            action: 'get_member_list',
            csrf_token: csrf_token,
        }).then(function (res) {
            if (res.data.code == 0) {
                thisvue.members = res.data.members;
            } else {
                thisvue.$alert(res.data.message, '获取成员失败');
            }
        }).catch(function (error) {
            thisvue.$alert(error, '获取成员失败');
        });
        this.status_long_polling();
    },
    beforeMount () {
        var userAgentInfo = navigator.userAgent;
        var Agents = ['Android', 'iPhone', 'SymbianOS', 'Windows Phone', 'iPad', 'iPod'];
        for (var v = 0; v < Agents.length; v++) {
            if (userAgentInfo.indexOf(Agents[v]) > 0) {
                this.isMobile = true
                break
            }
        }
    },
    destroyed: function () {
        this.leavePage = true;
    },
    computed: {
        damageHint: function () {
            if (this.damage < 10000) {
                return '';
            } else if (this.damage < 100000) {
                return '万';
            } else if (this.damage < 1000000) {
                return '十万';
            } else if (this.damage < 10000000) {
                return '百万';
            } else if (this.damage < 100000000) {
                return '千万';
            } else {
                return '`(*>﹏<*)′';
            }
        },
    },
    methods: {
        find_name: function (qqid) {
            for (m of this.members) {
                if (m.qqid == qqid) {
                    return m.nickname;
                }
            };
            return qqid;
        },
        status_long_polling: function () {
            var thisvue = this;
            axios.post("./api/", {
                action: 'update_boss',
                timeout: 30,
                csrf_token: csrf_token,
            }, {
                timeout: 40000,
            }).then(function (res) {
                if (res.data.code == 0) {
                    thisvue.bossData = res.data.bossData;
                    thisvue.base_cycle = res.data.base_cycle,
                    thisvue.status_long_polling();
                    if (res.data.notice) {
                        thisvue.$notify({
                            title: '通知',
                            message: '(' + (new Date()).toLocaleTimeString('chinese', { hour12: false }) + ') ' + res.data.notice,
                            duration: 60000,
                        });
                    }
                } else if (res.data.code == 1) {
                    thisvue.status_long_polling();
                } else {
                    thisvue.$confirm(res.data.message, '刷新boss数据错误', {
                        confirmButtonText: '重试',
                        cancelButtonText: '取消',
                        type: 'warning'
                    }).then(() => {
                        thisvue.status_long_polling();
                    }).catch(() => {
                    
                    });
                }
            }).catch(function (error) {
                if (thisvue.leavePage) {
                    return;
                }
                thisvue.$confirm(error, '刷新boss错误', {
                    confirmButtonText: '重试',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    thisvue.status_long_polling();
                }).catch(() => {

                });
            });
        },
        callapi: function (payload) {
            var thisvue = this;
            payload.csrf_token = csrf_token;
            axios.post("./api/", payload).then(function (res) {
                if (res.data.code == 0) {
                    if (res.data.bossData) {
                        thisvue.bossData = res.data.bossData;
                    }
                    if (res.data.base_cycle) {
                        thisvue.base_cycle = res.data.base_cycle;
                    }
                    if (res.data.notice) {
                        thisvue.$notify({
                            title: '通知',
                            message: res.data.notice,
                            duration: 60000,
                        });
                    }
                } else {
                    thisvue.$alert(res.data.message, 'Σ(っ °Д °;)っ');
                }
            }).catch(function (error) {
                thisvue.$alert(error, 'Σ(っ °Д °;)っ');
            });
        },
        update_boss_data: function() {
            this.callapi({
                action: 'update_boss_data'
            });
        },
        recordUndo: function (event) {
            this.callapi({
                action: 'undo',
            });
        },
        recordDamage: function (boss_num) {
            this.callapi({
                action: 'addrecord',
                defeat: this.defeat,
                behalf: this.behalf,
                damage: this.damage,
                boss_num: boss_num,
            });
            this.recordBehalfVisible = false;
        },
        challengeapply: function (boss_num) {
            this.callapi({
                action: 'apply',
                behalf: this.behalf_apply,
                is_continue: this.is_continue,
                boss_num: boss_num,
            });
        },
        cancelapply: function (event) {
            this.callapi({
                action: 'cancelapply',
                behalf: this.behalf_cancelApply,
            });
        },
        save_slot: function (event) {
            this.callapi({
                action: 'save_slot',
                member: this.slMember,
				status: true,
            });
        },
        cancel_save_slot: function (event) {
            this.callapi({
                action: 'save_slot',
                member: this.slMember,
				status: false,
            });
        },
        add_subscribe: function (event) {
            if(this.subscribe){
                this.callapi({
                    action: 'add_subscribe',
                    boss_num: parseInt(this.subscribe),
                    message: this.message,
                });
                this.subscribeFormVisible = false;
            } else {
                this.$alert('请选择一个boss');
            }
        },
        cancel_subscribe: function (event) {
            if(this.subscribe){
                this.callapi({
                    action: 'cancel_subscribe',
                    boss_num: parseInt(this.subscribe),
                });
                this.subscribeCancelVisible = false
            } else {
                this.$alert('请选择一个boss');
            }
        },
        startmodify: function (event) {
            if (this.is_admin) {
                this.statusFormVisible = true;
            } else {
                this.$alert('此功能仅公会战管理员可用');
            }
        },
        modify: function (event) {
            this.callapi({
                action: 'modify',
                cycle: this.base_cycle,
                bossData: this.bossData,
            });
            this.statusFormVisible = false;
        },
        put_on_the_tree: function(){
            this.callapi({
                action: 'put_on_the_tree',
                behalf: this.behalf_tree
            });
        },
        take_it_of_the_tree: function(){
            this.callapi({
                action: 'take_it_of_the_tree',
                behalf: this.behalf_cancelTree
            });
        },
        show_challengers: function(boss_num) {
            this.challengersList[boss_num] = true
        },
        close_challengers: function(boss_num) {
            this.challengersList[boss_num] = false
        },
        get_challenger_id: function(boss_num) {
            return "challengers_list" + String(boss_num)
        },
        get_boss_icon_id: function(boss_num) {
            return "boss_icon_num" + String(boss_num)
        },
        boss_icon_src: function(boss_num) {
            var icon_id = this.bossData[boss_num].icon_id
            return "/yobot-depencency/yocool@final/princessadventure/boss_icon/"+icon_id+".webp"
        },
        setting: function(){
            this.$router.push({path:'./setting/'})
        },
        handleSelect(key, keyPath) {
            this.leavePage = true;
            switch (key) {
                case '2':
                    window.location = './subscribers/';
                    break;
                case '3':
                    window.location = './progress/';
                    break;
                case '4':
                    window.location = './statistics/';
                    break;
                case '5':
                    window.location = `./${this.self_id}/`;
                    break;
                case '6':
                    window.location = `./clan-rank/`;
                    break;
            }
        },
    },
    delimiters: ['[[', ']]'],
})