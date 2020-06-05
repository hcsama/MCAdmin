<template>
    <span :class="statuscolor">
        {{serverstatus}}
    </span>
</template>

<script>
    export default {
        props: {
            status: {default: false},
        },
        data() {
            return {};
        },
        computed: {
            serverstatus() {
                const stati = { true: "Connected", false: "Not connected" };
                return stati[this.status];
            },
            statuscolor() {
                const colors = { true: "statusgreen", false: "statusred" };
                return colors[this.status];
            },
        }
    }
</script>

<style scoped>
    .statusgreen {
        border-radius: 25px;
        background: #73AD21;
        padding: 5px 10px;
        box-shadow: 0 0 15px rgb(173, 33, 33);
    }
    .statusred {
        border-radius: 25px;
        background: rgb(173, 33, 33);
        padding: 5px 10px; 
        box-shadow: 0 0 15px #73AD21;
    }
</style>