<template>
  <div class="load">
    <div>G</div>
    <div>N</div>
    <div>I</div>
    <div>D</div>
    <div>A</div>
    <div>O</div>
    <div>L</div>
  </div>
</template>
<style scoped>
.load {
    position: inline-block;
    width: 600px;
    height: 36px;
    overflow: visible;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    cursor: default;
}

.load div {
    position: absolute;
    width: 20px;
    height: 36px;
    opacity: 0;
    font-family: Helvetica, Arial, sans-serif;
    animation: move 4s linear infinite;
    -o-animation: move 4s linear infinite;
    -moz-animation: move 4s linear infinite;
    -webkit-animation: move 4s linear infinite;
    transform: rotate(180deg);
    -o-transform: rotate(180deg);
    -moz-transform: rotate(180deg);
    -webkit-transform: rotate(180deg);
    color: #a8a8a8;
}

.load div:nth-child(2) {
    animation-delay: 0.25s;
    -o-animation-delay: 0.25s;
    -moz-animation-delay: 0.25s;
    -webkit-animation-delay: 0.25s;
}

.load div:nth-child(3) {
    animation-delay: 0.5s;
    -o-animation-delay: 0.5s;
    -webkit-animation-delay: 0.5s;
    -webkit-animation-delay: 0.5s;
}

.load div:nth-child(4) {
    animation-delay: 0.75s;
    -o-animation-delay: 0.75s;
    -moz-animation-delay: 0.75s;
    -webkit-animation-delay: 0.75s;
}

.load div:nth-child(5) {
    animation-delay: 1.0s;
    -o-animation-delay: 1.0s;
    -moz-animation-delay: 1.0s;
    -webkit-animation-delay: 1.0s;
}

.load div:nth-child(6) {
    animation-delay: 1.25s;
    -o-animation-delay: 1.25s;
    -moz-animation-delay: 1.25s;
    -webkit-animation-delay: 1.25s;
}

.load div:nth-child(7) {
    animation-delay: 1.5s;
    -o-animation-delay: 1.5s;
    -moz-animation-delay: 1.5s;
    -webkit-animation-delay: 1.5s;
}

@keyframes move {
    0% {
        left: 0;
        opacity: 0;
    }

    35% {
        left: 41%;
        -moz-transform: rotate(0deg);
        -webkit-transform: rotate(0deg);
        -o-transform: rotate(0deg);
        transform: rotate(0deg);
        opacity: 1;
    }

    65% {
        left: 59%;
        -moz-transform: rotate(0deg);
        -webkit-transform: rotate(0deg);
        -o-transform: rotate(0deg);
        transform: rotate(0deg);
        opacity: 1;
    }

    100% {
        left: 100%;
        -moz-transform: rotate(-180deg);
        -webkit-transform: rotate(-180deg);
        -o-transform: rotate(-180deg);
        transform: rotate(-180deg);
        opacity: 0;
    }
}

@-moz-keyframes move {
    0% {
        left: 0;
        opacity: 0;
    }

    35% {
        left: 41%;
        -moz-transform: rotate(0deg);
        transform: rotate(0deg);
        opacity: 1;
    }

    65% {
        left: 59%;
        -moz-transform: rotate(0deg);
        transform: rotate(0deg);
        opacity: 1;
    }

    100% {
        left: 100%;
        -moz-transform: rotate(-180deg);
        transform: rotate(-180deg);
        opacity: 0;
    }
}

@-webkit-keyframes move {
    0% {
        left: 0;
        opacity: 0;
    }

    35% {
        left: 41%;
        -webkit-transform: rotate(0deg);
        transform: rotate(0deg);
        opacity: 1;
    }

    65% {
        left: 59%;
        -webkit-transform: rotate(0deg);
        transform: rotate(0deg);
        opacity: 1;
    }

    100% {
        left: 100%;
        -webkit-transform: rotate(-180deg);
        transform: rotate(-180deg);
        opacity: 0;
    }
}

@-o-keyframes move {
    0% {
        left: 0;
        opacity: 0;
    }

    35% {
        left: 41%;
        -o-transform: rotate(0deg);
        transform: rotate(0deg);
        opacity: 1;
    }

    65% {
        left: 59%;
        -o-transform: rotate(0deg);
        transform: rotate(0deg);
        opacity: 1;
    }

    100% {
        left: 100%;
        -o-transform: rotate(-180deg);
        transform: rotate(-180deg);
        opacity: 0;
    }
}
</style>
