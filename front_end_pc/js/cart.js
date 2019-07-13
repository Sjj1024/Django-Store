var vm = new Vue({
    el: '#app',
    data: {
        host,
        username: sessionStorage.username || localStorage.username,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        cart: [],
        total_selected_count: 0,
        origin_input: 0 // 用于记录手动输入前的值
    },
    computed: {
        total_count: function(){
            var total = 0;
            for(var i=0; i<this.cart.length; i++){
                total += parseInt(this.cart[i].count);
                this.cart[i].amount = (parseFloat(this.cart[i].price) * parseFloat(this.cart[i].count)).toFixed(2);
            }
            return total;
        },
        total_selected_amount: function(){
            var total = 0;
            this.total_selected_count = 0;
            for(var i=0; i<this.cart.length; i++){
                if(this.cart[i].selected) {
                    total += (parseFloat(this.cart[i].price) * parseFloat(this.cart[i].count));
                    this.total_selected_count += parseInt(this.cart[i].count);
                }
            }
            return total.toFixed(2);
        },
        selected_all: function(){
            var selected=true;
            for(var i=0; i<this.cart.length; i++){
                if(this.cart[i].selected==false){
                    selected=false;
                    break;
                }
            }
            return selected;
        }
    },
    mounted: function(){
        // 获取购物车数据
        axios.get(this.host+'/cart/', {
                headers: {
                    'Authorization': 'JWT ' + this.token
                },
                responseType: 'json',
                withCredentials: true
            })
            .then(response => {
                this.cart = response.data;
                for(var i=0; i<this.cart.length; i++){
                    this.cart[i].amount = (parseFloat(this.cart[i].price) * this.cart[i].count).toFixed(2);
                }
            })
            .catch(error => {
                console.log(error.response.data);
            })
    },
    methods: {
        // 退出
        logout: function(){
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },
        // 减少操作
        on_minus: function(index){
            if (this.cart[index].count > 1) {
                var count = this.cart[index].count - 1;
                this.update_count(index, count);
            }
        },
        on_add: function(index){
            var count = this.cart[index].count + 1;
            this.update_count(index, count);
        },
        on_selected_all: function(){
            var selected = !this.selected_all;
            for (var i=0; i<this.cart.length;i++){
                this.cart[i].selected = selected;
                this.update_count(i, this.cart[i].count);
            }
        },
        // 删除购物车数据
        on_delete: function(index){

        },
        on_input: function(index){
            var val = parseInt(this.cart[index].count);
            if (isNaN(val) || val <= 0) {
                this.cart[index].count = this.origin_input;
            } else {
                // 更新购物车数据
            }
        },
        // 更新购物车数据
        update_count: function(index, count){

        },
        // 更新购物车数据
        update_selected: function(index) {

        }
    }
});