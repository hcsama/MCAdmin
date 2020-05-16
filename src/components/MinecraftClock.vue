<template>
    <div class="box">
        <clock :time="time" :bg="daycolor" size="200px"/>
        <div class="text">
            <b>It is currently {{daytime}}</b>
        </div>
    </div>
</template>

<script>
    import Clock from 'vue-clock2';

    export default {
        components: { Clock },
        props: ['timevalue'],
        data() {
            return {};
        },
        computed: {
            hms() {
                return {
                    h: (Math.trunc((this.timevalue % 24000) / 1000) + 6) % 24,
                    m: Math.trunc((this.timevalue % 1000) * 60 / 1000),
                    s: Math.trunc((this.timevalue % 1000) * 3600 / 1000) % 60,
                }
            },
            time() {
                return this.hms.h.toString().concat(":").concat(this.hms.m.toString()).concat(":").concat(this.hms.s.toString())
            },
            daytime() {
                const h = this.hms.h;
                if(h == 0) {
                    return "midnight";
                }
                if(h < 7 || h > 18){ 
                    return "night";
                }
                if(h == 12) {
                    return "noon";
                }
                return "day";
            },
            daycolor() {
                const daycolors = {
                    "midnight": "#303030",
                    "night": "#A0A0F0",
                    "day": "#F8FF00",
                    "noon": '#FFFFE0',
                }
                return daycolors[this.daytime];
            },
        }
    }
</script>

<style scoped>
    .box {
        position: relative;
        display: inline-block;
    }
    .box .text {
        position: absolute;
        z-index: 999;
        margin: 0 auto;
        left: 0;
        right: 0;
        top: -30%;
        text-align: center;
        width: 60%;
    }
</style>