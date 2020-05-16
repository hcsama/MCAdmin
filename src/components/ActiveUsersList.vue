<template>
  <zing-grid
    ref="myGrid"
    :caption="caption"
    layout="row"
    pager
    page-size="5"
    control-bar="false"
    style="width: 100%;"
    sort
    height="180px"
    :data.prop="entries"
  >
    <zg-colgroup>
      <zg-column index="name" header="Player" type="text" ></zg-column>
      <zg-column index="uuid" header="UUID" type="text" ></zg-column>
    </zg-colgroup>
  </zing-grid>
</template>

<script>
export default {
  props: {
    actPlayers: { default: 0 },
    maxPlayers: { default: 0 },
    entries: Array,
  },
  data() {
    return {}
  },
  computed: {
    caption() {
      return 'Active Users ('.concat(this.actPlayers).concat('/').concat(this.maxPlayers).concat(')')
    }
  },
}
</script>
<style>

zg-head-cell {
  background: white;
  color: #5d7d9a;
  font-size: 1rem;
}
zg-row:nth-child(odd) {
  background: rgb(250, 250, 250);
}
zg-control-bar {
  display: none;
}
zg-caption {
color: #5d7d9a;
font-family: "Avenir", Helvetica, Arial, sans-serif;
font-weight: bold;
background: white;
padding-left: 0;
font-size: 1.4rem;
height: 54px;
text-align: left;

}
zing-grid {
  border: 1px;
  text-align: left;
}

zing-grid input[type="text"], zing-grid input[type="number"]{
  border-radius: 5px;
}

</style>
