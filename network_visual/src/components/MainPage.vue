<template>
  <div>
    <GraphD3 :isShowMainGraph="this.$store.state.showMainGraph"></GraphD3>
  </div>
</template>

<script>
import GraphD3 from "@/components/GraphD3";

export default {
  name: "MainPage",
  props:{
    msg:String
  },
  components:{
    GraphD3
  },
  methods:{
  }
}
</script>

