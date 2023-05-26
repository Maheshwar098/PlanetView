// import * as THREE from 'https://unpkg.com/three@0.152.2/build/three.module.js';
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  innerWidth / innerHeight,
  0.1,
  1000
)

const renderer = new THREE.WebGLRenderer({
  antialias : true,
  canvas : document.querySelector('canvas')
})
renderer.setPixelRatio(window.devicePixelRatio)

const canvasContainer = document.querySelector('#canvasContainer');

renderer.setSize(innerWidth, innerHeight)
// document.body.appendChild(renderer.domElement) //get rid of this 

const light = new THREE.DirectionalLight(0xffffff, 1)
light.position.set(2,2,5)
scene.add(light)

const sphere = new THREE.Mesh(new THREE.SphereGeometry(5, 50, 50), new THREE.MeshBasicMaterial({
      map : new THREE.TextureLoader().load('./assets/globe.jpg')
      })
  )
 
// scene.add(sphere)

// const group = new THREE.Group()
// group.add(sphere)
// scene.add(group)

const starGeometry = new THREE.BufferGeometry()
const starMaterial = new THREE.PointsMaterial({
  color:0xffffff
})

const starVertices = []
for(let i=0; i<10000; i++){
  const x = (Math.random() - 0.5)*2000
  const y = (Math.random() - 0.5)*2000
  const z = -Math.random()*1000
  starVertices.push(x, y, z)
}
starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3))

const stars = new THREE.Points(starGeometry, starMaterial)
scene.add(stars)

const group = new THREE.Group()
group.add(sphere)
group.add(stars)
scene.add(group)

let satellite;
const gltfloader = new THREE.GLTFLoader();
gltfloader.load('./assets/satellite/scene.gltf', (gltfScene) => {
  satellite = gltfScene;
  gltfScene.scene.rotation.x = 0.15;
  gltfScene.scene.rotation.y = 0.5;
  gltfScene.scene.rotation.z = 0.5;
  gltfScene.scene.position.x = 5;
  gltfScene.scene.position.z = 7;
  console.log(gltfScene.scene)
  // gltfScene.position.z = -7
  group.add(gltfScene.scene)
})
scene.add(group)

camera.position.z = 15

const mouse = {
  x : undefined,
  y : undefined
}

function animate() {
  requestAnimationFrame(animate)
  renderer.render(scene, camera)
  sphere.rotation.y += 0.005
  group.rotation.y = 0.5*mouse.x
  group.rotation.x = 0.5*mouse.y
  if(satellite){
    satellite.scene.rotation.z += 0.05
    satellite.scene.rotation.z += 0.05
  }
}

animate()

addEventListener('mousemove', ()=> {
  mouse.x = (event.clientX / innerWidth)*2 - 1
  mouse.y = -(event.clientY / innerHeight)*2 + 1
})