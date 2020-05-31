<template>
  <div id="app">
    <section class="dashboard">
      <header>
        <h1>Monitoring your Minecraft Server</h1>
      </header>
      <div class="dashboard_inputrow">
        <h3>
          Server <input style="margin-right:30px" v-model="serverip" placeholder="server address">
          Server Secret <input style="margin-right:30px" type=password v-model="serversecret" placeholder="server secret">
          <server-status :status="validconnectionparms"/>
        </h3>
      </div>
      <div class="dashboard__row">
        <digital :value="gamedays" caption="In-Game Days" />
        <digital :value="serveruptime" caption="Server Uptime" />
      </div>
      <div class="dashboard__row">
        <span>
          <minecraft-clock :timevalue="minecrafttime"/>
        </span>
        <span>
          <m-o-t-d v-bind:motd.sync="motd"/>
        </span>
      </div>
      <div class="dashboard__row">
        <users-list :entries="activePlayers" :maxPlayers="maxPlayers" :actPlayers="activePlayers.length"/>
      </div>
    </section>
  </div>
</template>

<script>
import UsersList from './components/UsersList.vue';
import MinecraftClock from './components/MinecraftClock.vue';
import ServerStatus from './components/ServerStatus.vue';
import MOTD from "./components/MOTD.vue";
import Digital from "./components/Digital.vue"
import axios from 'axios';
import _ from 'lodash';

export default {
  name: 'app',
  components: {
    UsersList,
    MinecraftClock,
    ServerStatus,
    MOTD,
    Digital,
  },
  data() {
    return {
      activePlayers: [],
      maxPlayers: 0,
      minecrafttime: 6000,
      serverip: '',
      serversecret: '',
      validconnectionparms: false,
      motd: '',
      gamedays: '-',
      serverup: 0,
      mcServer: process.env.VUE_APP_BE_URL || "/api/",
    };
  },
  computed: {
    serveruptime() {
      if(this.serverup == 0) {
        return '-';
      }
      const ticklen = 0.05;
      const secondticks = 1/ticklen;
      const minuteticks = 60*secondticks;
      const hourticks = 60*minuteticks;
      const dayticks = 24*hourticks;
      var runval = this.serverup;
      const days = Math.trunc(this.serverup / dayticks);
      runval -= dayticks * days;
      const hours = Math.trunc(runval / hourticks);
      runval -= hours*hourticks;
      const minutes = Math.trunc(runval / minuteticks);
      runval -= minutes*minuteticks;
      const seconds = Math.trunc(runval / secondticks);
      return days.toString() + 'd ' + hours.toString().padStart(2, ' ') + ':' + minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0')
    },
  },
  watch: {
    serverip() {
      this.debounced_setserverparms();
    },
    serversecret() {
      this.debounced_setserverparms();
    },
    motd() {
      const path = this.mcServer.concat('motd');
      const param = this.motd;
      axios.post(path, param).catch(e => { this.invalidateconnection(); });
    },
  },
  methods: {
    invalidateconnection() {
      this.processserverresult(false);
    },
    updateTime() {
      const path = this.mcServer.concat('time');
      axios.get(path).then((res) => {
        const n = res.data.daytime;
        if (n >= 0) { this.minecrafttime = n } else { this.minecrafttime = 6000 }
      }).catch(e => { this.invalidateconnection(); });
    },
    setserverparms() {
      const path = this.mcServer.concat('connect?serverip=').concat(this.serverip).concat('&serversecret=').concat(this.serversecret);
      axios.get(path).then((res) => { this.processserverresult(res.data.connected); }).catch(e => { this.invalidateconnection(); });
    },
    processserverresult(connected) {
      const before = this.validconnectionparms;
      this.validconnectionparms = connected;
      if(before != this.validconnectionparms) {
        if(before) {
          clearInterval(this.clockTimer);
          clearInterval(this.slowTimer);
          this.minecrafttime = 6000;
        }
        if(this.validconnectionparms) {
          this.clockTimer = setInterval(this.updateTime, 1000);
          this.slowTimer = setInterval(this.slowAction, 10000);
          this.slowAction();
        }
      }
    },
    slowAction() {
      this.updatePlayerlist();
      this.updateGameDays();
      this.updateServerUp();
    },
    updatePlayerlist() {
      const path = this.mcServer.concat('players');
      axios.get(path).then((res) =>{
        this.maxPlayers = res.data.maxplayers;
        this.activePlayers = res.data.players;
      }).catch(e => { this.invalidateconnection(); });
    },
    updateGameDays() {
      const path = this.mcServer.concat('days');
      axios.get(path).then((res) => {
        this.gamedays = res.data.days;
      }).catch(e => { this.invalidateconnection(); });
    },
    updateServerUp() {
      const path = this.mcServer.concat('serverup');
      axios.get(path).then((res) => {
        this.serverup = res.data.ticks;
      }).catch(e => { this.invalidateconnection(); });
    },
    setserverdefault() {
      const path = this.mcServer.concat('serverdefault');
      axios.get(path).then((res) => { this.serverip = res.data.serverdefault; this.serversecret = res.data.secretdefault; }).catch(e => { this.invalidateconnection(); });
    }
  },
  created() {
    this.debounced_setserverparms = _.debounce(this.setserverparms, 2000);
  },
  mounted() {
    this.setserverdefault();
    this.slowAction();
  },
  beforeDestroy() {
    clearInterval(this.clockTimer);
    clearInterval(this.slowTimer);
  }
}
</script>
