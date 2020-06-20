<template>
    <div class="tabs">
        <span v-for="tab in tabs" :key="tab.tab">
            <button v-if="tab.tab == currentTab" type="button" :name="tab.tab" class="active" v-on:click="clicktab()">{{ tab.label }}</button>
            <button v-else type="button" :name="tab.tab" v-on:click="clicktab()">{{ tab.label }}</button>
        </span>
        <span class="filler" />
    </div>
</template>

<script>
    export default {
        props: ['tabs', 'currentTab'],
        data() {
            return {
            };
        },
        computed: {
        },
        methods: {
            clicktab() {
                this.$emit('change-tab', {value: event.target.name});
            },
        },
    };
</script>

<style scoped>
    .tabs {
        display: flex;
        width: 100%;
        align-items: left;
    }
    .filler {
        width: 100%;
        border-bottom-style: solid;
        border-color: whitesmoke;
        border-width:  1px;
    }
    button {
        background: inherit;
        color: #F0F0F0;
        padding: 5px 10px;
        border-style: hidden hidden solid hidden;
        border-color: whitesmoke;
        border-width:  1px;
        margin-right: -1px;
        text-align: center;
        width: 200px;
        font-size: 1.5rem;
    }
    button:hover {
        background: rgb(98, 98, 99);
        cursor: pointer;
    }

    button:focus {
        outline: none;
    }

    .active {
        border-style: solid solid hidden solid;
        border-width:  1px;
    }
</style>