
var vm = new Vue({
    el: '#app',
    data: {
        isLoading: true,
        challengeData: [],
        activeIndex: '6',
        qqid: 0,
        nickname: '',
    },
    mounted() {
        var thisvue = this;
        var pathname = window.location.pathname.split('/');
        thisvue.qqid = parseInt(pathname[pathname.length - 2]);
        // axios.post('../api/', {
        //     action: 'get_user_challenge',
        //     csrf_token: csrf_token,
        //     qqid: thisvue.qqid,
        // }).then(function (res) {
        //     if (res.data.code != 0) {
        //         thisvue.$alert(res.data.message, '获取记录失败');
        //         return;
        //     }
        //     thisvue.nickname = res.data.user_info.nickname;
        //     thisvue.refresh(res.data.challenges, res.data.game_server);
        //     thisvue.isLoading = false;
        // }).catch(function (error) {
        //     thisvue.$alert(error, '获取数据失败');
        // });
    },
    methods: {
        handleSelect(key, keyPath) {
            switch (key) {
                case '1':
                    window.location = '../';
                    break;
                case '2':
                    window.location = '../subscribers/';
                    break;
                case '3':
                    window.location = '../progress/';
                    break;
                case '4':
                    window.location = '../statistics/';
                    break;
                case '5':
                    window.location = `../my/`;
                    break;
                case '6':
                    window.location = `../clan-rank/`;
                    break;
            }
        },
    },
    delimiters: ['[[', ']]'],
})