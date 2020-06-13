<template>
    <div class="usertable">
        {{ caption }}
        <vue-good-table ref="mytable" :columns="columns" :rows="curEntries" :selectOptions="selectOptions" styleClass="vgt-table condensed">
            <div slot="emptystate">
                - No players in list - 
            </div>
            <div slot="selected-row-actions">
              <button type="button" v-on:click="delaction()">Remove from whitelist</button>
            </div>
            <div v-if="changeable" slot="table-actions">
              <button type="button" v-on:click="addaction()">Add player</button>
              <input type="text" v-model="newPlayer">
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
        changeable: { type: Boolean, default: false },
        entries: Array,
    },
    data() {
        return {
          newPlayer: '',
          curEntries: [],
        }
    },
    watch: {
      entries() {
        if(this.entries.length != this.curEntries.length) {
          this.curEntries = this.entries;
        }
        else {
          for(var i in this.entries) {
            if(this.entries[i].name != this.curEntries[i].name) {
              this.curEntries = this.entries;
              return;
            } 
          }
        }
      },
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
      selectOptions() {
        if(this.changeable)
        {
          return {enabled: true};
        }
        else
        {
          return {enabled: false}
        }
      },
      caption() {
        return this.listCaption + ' (' + this.actPlayers +  (this.maxPlayers > 0 ? ('/' + this.maxPlayers) : '') + ')'
      },
    },
    methods: {
      addaction() {
        this.$emit('add-to-list', {player: this.newPlayer});
      },
      delaction() {
        this.$emit('del-from-list', this.$refs.mytable.selectedRows);
      },
    },
}
</script>

<style scoped>
  .usertable {
    margin: 20px 20px 0px;
  }
</style>
