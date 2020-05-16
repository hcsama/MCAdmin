<template>
   <zingchart :data="chartConfig"  :height="'100%'" ref="chart"/> 
</template>

<script>
export default {
  props: ['entries'],
  data() {
    return {
    };
  },
  computed: {
    values() {
      const categories = this.entries.reduce((acc, transaction) => {
         acc[transaction.purchase_type] = acc[transaction.purchase_type] || 0;
         acc[transaction.purchase_type]++;
         return acc;
         }, {});
      return Object.keys(categories).map((name) => {
        return {
          values: [categories[name]],
          text: name
        }
      })
    },
    chartConfig() {
      const colors = [
        {
          backgroundColor: '#04A3F5',
          hoverState: {
            backgroundColor: '#FF0000'
          }
        },
        {
          backgroundColor: '#98D1EE',
          hoverState: {
            backgroundColor: '#00FF00'
          }
        },
                {
          backgroundColor: '#295A73',
          hoverState: {
            backgroundColor: '#0000FF'
          }
        },
      ];
      const config ={
        type: 'pie',
        tooltip: {
          text: '%npv%'
        },
        plotarea: {
          margin: '5'
        },
        title: {
          text: 'Type distribution',
          adjustLayout: true,
          align: 'center',
          margin: 0,
          fontColor: '#5d7d9a'
        },
        plot: {
          valueBox: {
            fontSize: 10,
            text: '%t'
          },
          hoverState: {
         	  borderWidth: 2,
          }
        },
        // TODO: Format the data and pass it to the series.
        series: this.values.map((o, index) => Object.assign(o,colors[index])),
      };
      return config;
    },
  }
}
</script>
