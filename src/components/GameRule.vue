<template>
    <div class="gamerule">
        <input type="checkbox" :id="rule" :name="rule" :checked="ischecked" v-on:change="setvalue()">
        <label :for="rule">{{ruledesc}}</label>
    </div>
</template>

<script>
    export default {
        props: ['rule', 'ruledesc', 'rulelist'],
        data() {
            return {
            };
        },
        computed: {
            ischecked() {
                return this.rulelist[this.rule].value;
            }
        },
        methods: {
            setvalue() {
                this.$emit('set-rule-val', {rule: this.rule, value: event.target.checked});
            },
        },
    };
</script>

<style scoped>
    .gamerule {
        background: rgb(98, 98, 99);
        padding: 5px 10px;
        border-style: solid;
        border-color: whitesmoke;
        border-width:  2px;
        margin: 0px 10px;
        text-align: left;
    }
</style>