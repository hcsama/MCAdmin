<template>
    <div>
        {{ caption }}
        <vue-good-table :columns="columns" :rows="entries">
            <div slot="emptystate">
                - No active players -
            </div>
        </vue-good-table>
    </div>
</template>

<script>
import 'vue-good-table/dist/vue-good-table.css';
import { VueGoodTable } from 'vue-good-table';

export default {
    components: { VueGoodTable },
    props: {
        actPlayers: { default: 0 },
        maxPlayers: { default: 0 },
        entries: Array,
    },
    data() {
        return {
            columns: [
                        {label: "Player",
                         field: "name",
                         sortable: true,
                         type: "text"},
                        {label: "UUID",
                         field: "uuid",
                         sortable: true,
                         type: "text"},
            ],
        }
    },
    computed: {
        caption() {
        return 'Active Users ('.concat(this.actPlayers).concat('/').concat(this.maxPlayers).concat(')')
        }
    },
}
</script>

<style scoped>
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
