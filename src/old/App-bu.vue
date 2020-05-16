<template>
  <div id="app">
    <section class="dashboard">
      <header>
        <!-- date range placeholder -->
        <h4>Date Range</h4>
        <v-date-picker mode="range" v-model="rangeToShow" />
      </header>
      <div v-for="currency in info" class="dashboard">
        {{currency.description}}:
          <span v-html="currency.symbol" />{{currency.rate_float.toFixed(2)}}
      </div>
      <div class="dashboard__row">
        <latest-transactions-chart ref="latestTransactions" :entries="filteredTransactions" />
        <transaction-breakdown-chart ref="transactionBreakdown" :entries="filteredTransactions" />
      </div>
      <div class="dashboard__row">
        <transaction-details-grid :entries="filteredTransactions"/>
      </div>
    </section>
  </div>
</template>

<script>
import transactions from './data/transactions.js';

import LatestTransactionsChart from './components/LatestTransactionsChart.vue';
import TransactionBreakdownChart from './components/TransactionBreakdownChart.vue';
import TransactionDetailsGrid from './components/TransactionDetailsGrid.vue';

import axios from 'axios';

export default {
  name: 'app',
  components: {
    LatestTransactionsChart,
    TransactionBreakdownChart,
    TransactionDetailsGrid,
  },
  data() {
    return {
      transactions,
      info: 'Loading...',
      rangeToShow: {
        start: new Date().setTime(transactions.reduce((min, t) => Math.min(min, t.timestamp), transactions[0].timestamp)),
        end: new Date().setTime(transactions.reduce((max, t) => Math.max(max, t.timestamp), transactions[0].timestamp))
      }
    };
  },
  computed: {
    filteredTransactions() {
      return this.transactions.filter(entry => {
        return (entry.timestamp >= this.rangeToShow.start && entry.timestamp < this.rangeToShow.end );
      });
    },
  },
  methods: {

  },
  mounted() {
    axios.get('https://api.coindesk.com/v1/bpi/currentprice.json').then(response => (this.info = response.data.bpi));
  }
}
</script>
