<template>
    <div class="box" >
        <clock :time="time" :bg="daycolor" :color="textcolor" size="170px"/>
        <div class="text">
            <b>- {{daytime}} -</b>
        </div>
    </div>
</template>

<script>
    import Clock from 'vue-clock2';

    export default {
        components: { Clock },
        props: ['timevalue'],
        data() {
                return {
                    daycolors: {
                        midnight: { d: "#303030", t: "#F0F0F0"},
                        night: { d: "#3030A0", t: "#F0F0F0"},
                        daytime: { d: "#F8FF00", t: "#101010"},
                        noon: { d: '#FFFFE0', t: "#101010"},
                    },
                }
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
                return "daytime";
            },
            daycolor() {
                return this.daycolors[this.daytime].d;
            },
            textcolor() {
                return this.daycolors[this.daytime].t;
            },
        }
    }
</script>

<style scoped>
    .box {
        position: relative;
        display: inline-block;
        color: #101010;
    }
    .box .text {
        color: #F0F0F0;
        font-size: 1.5rem;
        position: absolute;
        z-index: 999;
        margin: 0 auto;
        left: 0;
        right: 0;
        top: -25%;
        text-align: center;
        width: 80%;
    }
</style>