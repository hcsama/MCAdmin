<template>
    <div id="clock">
        <p class="date">{{ caption }}</p>
        <p class="time">{{ value }}</p>
        <p class="text">Updated every 10 seconds</p>
    </div>
</template>

<script>
    export default {
        props: ['value', 'caption'],
        data() {
            return {
            };
        },
        computed: {
        },
        methods: {
        }
    }
</script>

<style lang="scss" scoped>
p {
    margin: 0;
    padding: 0;
}
#clock {
    width: 30%;
    font-family: 'Share Tech Mono', monospace;
    text-align: center;
    color: #d7dfe2;
    text-shadow: 0 0 15px rgb(62, 74, 253);
    .time {
        letter-spacing: 0.05em;
        font-size: 60px;
        padding: 0px 0;
    }
    .date {
        letter-spacing: 0.1em;
        font-size: 20px;
    }
    .text {
        letter-spacing: 0.1em;
        font-size: 10px;
        padding: 0px 0 0;
    }
}
</style>