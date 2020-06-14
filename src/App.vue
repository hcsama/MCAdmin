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
        <digital :value="gamedays" caption="In-Game Days" />
        <digital :value="serveruptime" caption="Server Uptime" />
      </div>
      <div class="dashboard__row">
        <users-list listCaption="Active Players" :entries="activePlayers" :maxPlayers="maxPlayers" :actPlayers="activePlayers.length"/>
        <users-list listCaption="Whitelisted Players" :entries="whitelistPlayers" :actPlayers="whitelistPlayers.length" :changeable="true" v-on:add-to-list="addwhitelist($event)" v-on:del-from-list="delwhitelist($event)"/>
      </div>
      <div class="dashboard__row">
        <span style="color: red;">
          {{ returnMessage }}
        </span>
      </div>
      <div class="dashboard__row">
        <img-button cmd="day" image="day.png" labeltext="Set day" v-on:img-button-event="setdaytime($event)" />
        <img-button cmd="night" image="night.png" labeltext="Set night" v-on:img-button-event="setdaytime($event)" />
        <img-button cmd="clear" image="day.png" labeltext="Clear weather" v-on:img-button-event="setweather($event)" />
        <img-button cmd="rain" image="snow.png" labeltext="Make rain/snow" v-on:img-button-event="setweather($event)" />
        <img-button cmd="thunder" image="snow.png" labeltext="Make thunderstorm" v-on:img-button-event="setweather($event)" />
        <span>
          <m-o-t-d v-bind:motd.sync="motd"/>
        </span>
      </div>
      <div v-for="row in Math.trunc(vforrules.length/3)+1" class="dashboard__row" style="margin:10px">
        <template v-for="i in 3">
          <game-rule v-if="i-1+(row-1)*3 < vforrules.length" :rule=vforrules[i-1+(row-1)*3].rule :ruledesc=vforrules[i-1+(row-1)*3].desc :rulelist="rules" v-on:set-rule-val="setruleval($event)"/>
        </template>
      </div>
    </section>
  </div>
</template>

<script>
import UsersList from './components/UsersList.vue';
import MinecraftClock from './components/MinecraftClock.vue';
import ServerStatus from './components/ServerStatus.vue';
import MOTD from "./components/MOTD.vue";
import Digital from "./components/Digital.vue";
import GameRule from "./components/GameRule.vue";
import ImgButton from "./components/ImgButton.vue";

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
    GameRule,
    ImgButton,
  },
  data() {
    return {
      activePlayers: [],
      whitelistPlayers: [],
      maxPlayers: 0,
      minecrafttime: 6000,
      serverip: '',
      serversecret: '',
      validconnectionparms: false,
      motd: '',
      gamedays: '-',
      returnMessage: '',
      serverup: 0,
      mcServer: process.env.VUE_APP_BE_URL || "/api/",
      rules: {
        keepInventory: {value: '', desc: 'Keep inventory & experience after death', type: 'gamerule'},
        doLimitedCrafting: {value: '', desc: 'Players can only craft recipies they have learned', type: 'gamerule'},
        enforceWhitelist: {value: '', desc: 'Only whitelisted players allowed', type: 'whitelist'},
        doDaylightCycle: {value: '', desc: 'Day and night happening', type: 'gamerule'},
        doWeatherCycle: {value: '', desc: 'Weather can change', type: 'gamerule'},
        drowningDamage: {value: '', desc: 'Players can drown', type: 'gamerule'},
        fallDamage: {value: '', desc: 'Players can die from a fall', type: 'gamerule'},
        fireDamage: {value: '', desc: 'Fire will burn players', type: 'gamerule'},
        naturalRegeneration: {value: '', desc: 'Players regenerate health with normal food', type: 'gamerule'},
      },
    };
  },
  computed: {
    vforrules() {
      var vfor = [];
      for(const r in this.rules) {
        const v = { rule: r, desc: this.rules[r].desc };
        vfor.push(v);
      }
      return vfor;
    },
    rulev(r) {
      return '';
    },
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
      axios.post(path, param).then((res) => { this.returnMessage = 'Sent message to all: ' + param }).catch(e => { this.invalidateconnection(); });
    },
    returnMessage() {
      if(this.returnMessage != ''){
        this.debounced_clearmsg();
      }
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
      const path = this.mcServer + 'connect?serverip=' + this.serverip + '&serversecret=' + this.serversecret;
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
          this.uponServerConnect();
        }
      }
    },
    uponServerConnect() {
      this.slowAction();
      this.updateGameRules();
    },
    slowAction() {
      this.updatePlayerlist();
      this.updateWhitelist();
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
    updateWhitelist() {
      const path = this.mcServer.concat('whitelist');
      axios.get(path).then((res) =>{
        this.whitelistPlayers = res.data.players;
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
    },
    updateruleval(rule, value) {
      if(value == 'true') {
          this.rules[rule].value = 'on';
        }
      else if(value == 'false') {
          this.rules[rule].value = '';
        }
      else if(value == 'ERROR') {
        console.log('rule ' + rule + ' ' + value);
      }
    },
    getruleval(event) {
      switch (this.rules[event.rule].type) {
        case 'gamerule':
          var path = this.mcServer + 'gamerule?rule=' + event.rule;
          axios.get(path).then((res) => { this.updateruleval(event.rule, res.data.value); }).catch(e => { this.invalidateconnection() });
          break;      
        case 'whitelist':
          var path = this.mcServer + 'whitelistonoff';
          axios.get(path).then((res) => { this.updateruleval(event.rule, res.data.value); }).catch(e => { this.invalidateconnection() });
          break;      
        default:
          break;
      }
    },
    setruleval(event) {
      switch (this.rules[event.rule].type) {
        case 'gamerule':
          var path = this.mcServer + 'gamerule?rule=' + event.rule + '&value=' + event.value;
          axios.get(path).then((res) => { this.updateruleval(event.rule, res.data.value) }).catch(e => { this.invalidateconnection() });
          break;
        case 'whitelist':
          var path = this.mcServer + 'whitelistonoff?value=' + event.value;
          axios.get(path).then((res) => { this.updateruleval(event.rule, res.data.value); }).catch(e => { this.invalidateconnection() });
          break;      
        default:
          break;
      }
    },
    updateGameRules() {
      for(const rule in this.rules) {
        this.getruleval({rule: rule});
      }
    },
    setdaytime(event) {
      const path = this.mcServer.concat('daytime');
      const param = {cmd: event.cmd};
      axios.post(path, param).then((res) => { this.returnMessage = res.data.msg }).catch(e => { this.invalidateconnection(); });
    },
    setweather(event) {
      const path = this.mcServer.concat('weather');
      const param = {cmd: event.cmd};
      axios.post(path, param).then((res) => { this.returnMessage = res.data.msg }).catch(e => { this.invalidateconnection(); });
    },
    clearmsg() {
      this.returnMessage = '';
    },
    addwhitelist(event) {
      const path = this.mcServer.concat('addwhitelist');
      const param = {name: event.player};
      axios.post(path, param).then(res => {
          if(res.status != 200) {
            this.returnMessage = param.name + ' is not a known player name';
          }
          else {
            this.updateWhitelist();
            this.returnMessage = res.data.msg;
          }
          }).catch(e => { this.invalidateconnection(); });
    },
    delwhitelist(event) {
      if(event.length != 1)
      {
        this.returnMessage = 'May only remove exactly one player each time';
        return;
      }
      var players = [];
      for (var p in event)
      {
        players.push(event[p].name);
      }
      const path = this.mcServer.concat('delwhitelist');
      const param = {names: players};
      axios.post(path, param).then(res => { this.returnMessage = res.data.msg; this.updateWhitelist(); }).catch(e => { this.invalidateconnection(); });
    },
  },

  created() {
    this.debounced_setserverparms = _.debounce(this.setserverparms, 2000);
    this.debounced_clearmsg = _.debounce(this.clearmsg, 3000);
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
