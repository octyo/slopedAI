let speedConfig = {
  speed: 0.01,
  cbSetIntervalChecked: true,
  cbSetTimeoutChecked: true,
  cbPerformanceNowChecked: true,
  cbDateNowChecked: true,
  cbRequestAnimationFrameChecked: true,
};

const emptyFunction = () => {};

const originalDateNow = Date.now;

const originalRequestAnimationFrame = window.requestAnimationFrame;

// requestAnimationFrame
(function () {
  let dateNowValue = null;
  let previusDateNowValue = null;
  const callbackFunctions = [];
  const callbackTick = [];
  const newRequestAnimationFrame = (callback) => {
    return originalRequestAnimationFrame((timestamp) => {
      const originalValue = originalDateNow();
      if (dateNowValue) {
        dateNowValue +=
          (originalValue - previusDateNowValue) *
          (speedConfig.cbRequestAnimationFrameChecked
            ? speedConfig.speed
            : 1);
      } else {
        dateNowValue = originalValue;
      }
      previusDateNowValue = originalValue;

      const dateNowValue_MathFloor = Math.floor(dateNowValue);

      const index = callbackFunctions.indexOf(callback);
      let tickFrame = null;
      if (index == -1) {
        callbackFunctions.push(callback);
        callbackTick.push(0);
        callback(dateNowValue_MathFloor);
      } else if (speedConfig.cbRequestAnimationFrameChecked) {
        tickFrame = callbackTick[index];
        tickFrame += speedConfig.speed;

        if (tickFrame >= 1) {
          while (tickFrame >= 1) {
            callback(dateNowValue_MathFloor);
            window.requestAnimationFrame = emptyFunction;
            tickFrame -= 1;
          }
          window.requestAnimationFrame = newRequestAnimationFrame;
        } else {
          window.requestAnimationFrame(callback);
        }
        callbackTick[index] = tickFrame;
      } else {
        callback(dateNowValue_MathFloor);
      }
    });
  };
  window.requestAnimationFrame = newRequestAnimationFrame;
})();

window.addEventListener("message", (e) => {
  if (e.data.command === "getSpeedConfig") {
    window.postMessage({
      command: "setSpeedConfig",
      config: speedConfigNew,
    });
  }
});
