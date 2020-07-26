export function nextAnimationFrame() {
  let animationFrameId;
  let promise = new Promise(resolve => {
    animationFrameId = requestAnimationFrame(resolve);
  });
  promise.__ec_cancel__ = () => {
    cancelAnimationFrame(animationFrameId);
  };
  return promise;
}
