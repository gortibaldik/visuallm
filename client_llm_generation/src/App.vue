<template>
  <nav>
    <router-link class="button" to="/">Next Token Prediction</router-link>
    <router-link class="button" to="/connections">Connections</router-link>
  </nav>
  <main>
    <router-view></router-view>
  </main>
</template>

<style scoped>
nav {
  margin-bottom: 10px;
}

.button {
  background-color: rgba(0, 0, 0, 0.409);
  padding: 10px;
  border-radius: 5px;
  color: black;
  margin-right: 2px;
}

.router-link-active {
  background-color: rgba(0, 0, 0, 0.3);
  color: rgb(87, 42, 42);
}
</style>