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
        <span>
          <minecraft-clock :timevalue="minecrafttime"/>
        </span>
        <active-users-list :entries="activePlayers" :maxPlayers="maxPlayers" :actPlayers="activePlayers.length"/>
      </div>
      <div class="dashboard__row">
        <span>
          <m-o-t-d v-bind:motd.sync="motd"/>
        </span>
      </div>
    </section>
  </div>
</template>

<script>
import ActiveUsersList from './components/ActiveUsersList.vue';
import MinecraftClock from './components/MinecraftClock.vue';
import ServerStatus from './components/ServerStatus.vue';
import MOTD from "./components/MOTD.vue";
import axios from 'axios';
const mcServer = '/api/'

export default {
  name: 'app',
  components: {
    ActiveUsersList,
    MinecraftClock,
    ServerStatus,
    MOTD,
  },
  data() {
    return {
      activePlayers: [],
      maxPlayers: 0,
      minecrafttime: 6000,
      serverip: '192.168.1.49',
      serversecret: '',
      validconnectionparms: false,
      motd: '',
    };
  },
  computed: {
  },
  watch: {
    serverip() {
      this.setserverparms();
    },
    serversecret() {
      this.setserverparms();
    },
    motd() {
      const path = mcServer.concat('motd');
      const param = this.motd;
      axios.post(path, param).catch(e => { this.invalidateconnection(); });
    },
  },
  methods: {
    invalidateconnection() {
      processserverresult(false);
    },
    updateTime() {
      const path = mcServer.concat('time');
      axios.get(path).then((res) => {
        const n = res.data.daytime;
        if (n >= 0) { this.minecrafttime = n } else { this.minecrafttime = 6000 }
      }).catch(e => { this.invalidateconnection(); });
    },
    setserverparms() {
      const path = mcServer.concat('connect?serverip=').concat(this.serverip).concat('&serversecret=').concat(this.serversecret);
      axios.get(path).then((res) => { this.processserverresult(res.data.connected); }).catch(e => { this.invalidateconnection(); });
    },
    processserverresult(connected) {
      const before = this.validconnectionparms;
      this.validconnectionparms = connected;
      if(before != this.validconnectionparms) {
        if(before) {
          clearInterval(this.clockTimer);
          clearInterval(this.playerTimer);
        }
        if(this.validconnectionparms) {
          this.clockTimer = setInterval(this.updateTime, 1000);
          this.playerTimer = setInterval(this.updatePlayerlist, 10000);
        }
      }
    },
    updatePlayerlist() {
      const path = mcServer.concat('players');
      axios.get(path).then((res) =>{
        this.maxPlayers = res.data.maxplayers;
        this.activePlayers = res.data.players;
      }).catch(e => { this.invalidateconnection(); });
    },
  },
  mounted() {
    this.setserverparms();
  },
  beforeDestroy() {
    clearInterval(this.clockTimer);
    clearInterval(this.playerTimer);
  }
}
</script>
