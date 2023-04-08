var vm = new Vue({
    el: '#app',
    data: {
        setting: {},
        activeNames: [],
        bossSetting: false,
        domain: '',
        domainApply: false,
        applyName: '',
        loading: false,
        boss_id_name: {}
    },
    mounted() {
        var thisvue = this;
        axios.get(api_path).then(function (res) {
            if (res.data.code == 0) {
                thisvue.setting = res.data.settings;
                thisvue.boss_id_name = res.data.boss_id_name;
            } else {
                alert(res.data.message);
            }
        }).catch(function (error) {
            alert(error);
        });
    },
    methods: {
        update: function (event) {
            var flag = this.check_level_by_cycle()
            if (!flag) {
                alert('阶段对应周目错误。\n不同阶段的周目范围不能重叠，且下阶段开始周目必须等于上阶段结束周目加一');
                return
            }
            this.setting.web_mode_hint = false;
            axios.put(
                api_path,
                {
                    setting: this.setting,
                    csrf_token: csrf_token,
                },
            ).then(function (res) {
                if (res.data.code == 0) {
                    alert('设置成功，重启机器人后生效');
                } else {
                    alert('设置失败：' + res.data.message);
                }
            }).catch(function (error) {
                alert(error);
            });
        },
        sendApply: function (api) {
            if (this.domain === '') {
                alert('请选择后缀');
                return;
            }
            if (/^[0-9a-z]{1,16}$/.test(this.applyName)) {
                ;
            } else {
                alert('只能包含字母、数字');
                return;
            }
            var thisvue = this;
            this.loading = true;
            axios.get(
                api + '?name=' + thisvue.applyName + thisvue.domain
            ).then(function (res) {
                thisvue.domainApply = false;
                if (res.data.code == 0) {
                    alert('申请成功，请等待1分钟左右解析生效');
                    thisvue.setting.public_address = thisvue.setting.public_address.replace(/\/\/([^:\/]+)/, '//' + thisvue.applyName + thisvue.domain);
                    thisvue.update(null);
                } else if (res.data.code == 1) {
                    alert('申请失败，此域已被占用');
                } else {
                    alert('申请失败，' + res.data.message);
                }
                thisvue.loading = false;
            }).catch(function (error) {
                thisvue.loading = false;
                alert(error);
            });
        },
        comfirm_change_clan_mode: function (event) {
            this.$alert('修改模式后，公会战数据会重置。请不要在公会战期间修改！', '警告', {
                confirmButtonText: '知道了',
                type: 'warning',
            });
        },
        add_level: function (area) {
            this.setting.boss[area].push([0, 0, 0, 0, 0]);
            this.setting.level_by_cycle[area].push([0, 0]);
        },
        remove_level: function (area) {
            this.setting.boss[area].pop();
            this.setting.level_by_cycle[area].pop();
        },
        check_level_by_cycle: function () {
            for (const area in this.setting.level_by_cycle) {
                var last_level_max = 0
                for (const level_info of this.setting.level_by_cycle[area]) {
                    if (level_info[0] != last_level_max + 1 || level_info[0] > level_info[1])
                        return false
                    last_level_max = level_info[1]
                }
            }
            return true
        }
    },
    delimiters: ['[[', ']]'],
})