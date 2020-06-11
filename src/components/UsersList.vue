<template>
    <div class="usertable">
        {{ caption }}
        <vue-good-table :columns="columns" :rows="entries" styleClass="vgt-table condensed">
            <div slot="emptystate">
                - No players in list - 
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
        listCaption: String,
        entries: Array,
    },
    data() {
        return {
        }
    },
    computed: {
        columns() {
            var cols = [{label: "Player",
                         field: "name",
                         sortable: true,
                         type: "text"},
                    ];
            if(this.entries.length > 0 && 'uuid' in this.entries[0])
            {
              cols.push({label: "UUID",
                         field: "uuid",
                         sortable: true,
                         type: "text"});
            }
            return cols;

        },
        caption() {
        return this.listCaption + ' (' + this.actPlayers +  (this.maxPlayers > 0 ? ('/' + this.maxPlayers) : '') + ')'
        }
    },
}
</script>

<style scoped>
  .usertable {
    margin: 20px 20px 0px;
  }
</style>
