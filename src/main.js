import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false;

// import the zingchart-vue component, which in turn, imports the zingchart library itself.
import zingchartVue from 'zingchart-vue';
Vue.component('zingchart', zingchartVue);

// Import the ZingGrid library, By default, the ZingGrid library registers itself as a web component.
import ZingGrid from "zinggrid";

new Vue({
  render: h => h(App),
}).$mount('#app');
