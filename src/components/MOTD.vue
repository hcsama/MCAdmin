<template>
    <div class="box">
        <textarea rows="4" cols="40" maxlength="100" v-model="msg">Enter message here</textarea>
        <div class="above">
            Send message to all
        </div>
        <div class="below">
            <button style="margin:0px 30px;max-width:100px;" type="button" v-on:click="sendmotd" >Send message</button>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                msg: '',
            };
        },
        computed: {
        },
        methods: {
            sendmotd() {
                this.$emit('update:motd', this.msg);
                this.msg = '';
            }
        }
    }
</script>

<style scoped>
    .box {
        position: relative;
        display: inline-block;
    }
    .below {
        position: absolute;
        z-index: 999;
        margin: 0 auto;
        left: 0;
        right: 0;
        top: 100%;
        text-align: center;
        width: 60%;
    }
    .above {
        position: absolute;
        z-index: 999;
        margin: 0 auto;
        left: 0;
        right: 0;
        top: -40%;
        text-align: left;
        width: 60%;
    }
</style>