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
    }
    .statusred {
        border-radius: 25px;
        background: rgb(173, 33, 33);
        color: #a2d1ff;
        padding: 5px 10px; 
    }
</style>