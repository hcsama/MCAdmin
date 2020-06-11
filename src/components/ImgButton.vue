<template>
    <div class="imgbutton">
        <input type="image" :id="cmd" v-on:click="telldaddy()" :src="image" width="124" height="70">
        <label :for="cmd">{{labeltext}}</label>
    </div>
</template>

<script>
    export default {
        props: ['cmd', 'labeltext', 'image'],
        data() {
            return {
            };
        },
        computed: {
            bgimage() {
                return 'background-image: url(' + this.image + ');'
            },
        },
        methods: {
            telldaddy() {
                this.$emit('img-button-event', {cmd: this.cmd});
            },
        },
    };
</script>

<style scoped>
    .imgbutton {
        padding: 5px 10px;
        margin: 0px 10px;
        width: 150px;
        text-align: left;
        display: flex;
        justify-content: center;
        position: relative;
    }

    .imgbutton input {
        border-style: solid;
        border-width:  2px;
    }

    .imgbutton input:hover {
        border-style: solid;
        border-color: whitesmoke;
        border-width:  2px;
    }

    .imgbutton label {
        position: absolute;
        text-align: center;
        bottom: -10px;
        width: 100%;
        text-shadow: 0px 0px 5px black;
        font-weight: bold;
    }
</style>