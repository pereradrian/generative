import '../style.css'

import { MathUtils, Scene } from 'three'
import { PerspectiveCamera } from 'three'
import { WebGLRenderer } from 'three'
import { TorusGeometry } from 'three'
import { MeshStandardMaterial } from 'three'
import { MeshBasicMaterial } from 'three'
import { Mesh } from 'three'
import { PointLight } from 'three'
import { AmbientLight } from 'three'
import { PointLightHelper } from 'three'
import { GridHelper } from 'three'

import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { SphereGeometry } from 'three'
import { Texture } from 'three'
import { TextureLoader } from 'three'
import { BoxGeometry } from 'three'
import { BufferGeometry } from 'three'
import { BufferAttribute } from 'three'
import { TubeGeometry } from 'three'
import { Curve } from 'three'
import { Vector3 } from 'three'

const FIELD_VIEW = 75
const ASPECT_RATIO = window.innerWidth / window.innerHeight
const NEAR_THRESHOLD = 0.1
const FAR_THRESHOLD = 10000
const CAMERA_HEIGHT = 30

const scene = new Scene();
const camera = new PerspectiveCamera(FIELD_VIEW, ASPECT_RATIO,
  NEAR_THRESHOLD, FAR_THRESHOLD);

const renderer = new WebGLRenderer({
  canvas: document.querySelector('#background'),
});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
camera.position.setZ(CAMERA_HEIGHT);


// Object
const RADIUS = 10;
const TUBE = 3;
const RADIAL_SEGMENTS = 60;
const TUBULAR_SEGMENTS = 100;
const geometry = new TorusGeometry(RADIUS, TUBE, RADIAL_SEGMENTS, TUBULAR_SEGMENTS);
// const material = new MeshBasicMaterial({ color: 0xFF6347, wireframe: true });
const material = new MeshStandardMaterial({ color: 0xFF6347});
const torus = new Mesh(geometry, material);
scene.add(torus);

// Light
const LIGHT_ORIGIN_X = 20;
const LIGHT_ORIGIN_Y = 5;
const LIGHT_ORIGIN_Z = 5;
const pointLight = new PointLight(0xffffff);
pointLight.position.set(LIGHT_ORIGIN_X, LIGHT_ORIGIN_Y, LIGHT_ORIGIN_Z);
scene.add(pointLight);

const ambientLight = new AmbientLight(0xffffff);
//scene.add(ambientLight);

const lightHelper = new PointLightHelper(pointLight);
//scene.add(lightHelper);

const GRID_HELPER_SIZE = 200;
const GRID_HELPER_DIVISIONS = 50;
const gridHelper = new GridHelper(GRID_HELPER_SIZE, GRID_HELPER_DIVISIONS);
//scene.add(gridHelper);

// Interaction
const controls = new OrbitControls(camera, renderer.domElement);

// Populating
function addStar() {
  const sphereRadius = 0.25;
  const widthSegments = 24;
  const heightSegments = 24;
  const geometry = new SphereGeometry(sphereRadius, widthSegments, heightSegments);
  const material = new MeshStandardMaterial( {color : 0xffffff});
  const star = new Mesh(geometry, material);

  const [x,y,z] = Array(3).fill().map(() => MathUtils.randFloatSpread(100)); 

  star.position.set(x,y,z);
  scene.add(star);
}
//Array(200).fill().forEach(addStar);

const backgroundTexture = new TextureLoader().load('resources/img/space_earth.png');
scene.background = backgroundTexture

const dist = 5.0
const center_x = 0.0
const center_y = 0.0
const center_z = -20*dist

class Monke {
  constructor(mesh,x, y, z) {
    this.mesh = mesh;
    this.v_x = MathUtils.randFloatSpread(0.05);
    this.v_y = MathUtils.randFloatSpread(0.05);
    this.v_z = MathUtils.randFloatSpread(0.05);
    this.x = x;
    this.y = y;
    this.z = z;
    //this.label = new TextGeometry(`${x}, ${y}, ${z}`);
    mesh.position.set(x + center_x,y + center_y,z + center_z);
    //this.label.position.set(x,y,z);
  }
}

class CustomTube extends Curve {
	constructor( scale = 1 ) {
		super();
		this.scale = scale;
	}

	getPoint( t, optionalTarget = new Vector3() ) {
		const tx = 0;
		const ty = 0;
		const tz = t;
		return optionalTarget.set( tx, ty, tz ).multiplyScalar( this.scale );

	}
}

const path = new CustomTube( 10 );
const tubeGeometry = new TubeGeometry( path, 20, 2, 8, false );
const tubeMaterial = new MeshBasicMaterial( { color: 0x00ff00 } );
const mesh = new Mesh( tubeGeometry, tubeMaterial );
//scene.add( mesh );

// Object
const lineGeometry = new TubeGeometry();
const vertices = new Float32Array( [
  0.0, 0.0,  0.0,
	 0.0, 0.0,  dist
] );

// itemSize = 3 because there are 3 values (components) per vertex
lineGeometry.setAttribute( 'position', new BufferAttribute( vertices, 3 ) )
const lineMaterial = new MeshStandardMaterial({ color: 0xFF6347});
const lineMesh = new Mesh( lineGeometry, lineMaterial );
scene.add(lineMesh);

// Monke
// Add monkes
function addMonke(x,y,z) {
  const monkeSize = MathUtils.randFloatSpread(dist)+dist;
  const monkeTexture = new TextureLoader().load('resources/img/orange.jpg');
  const mesh = new Mesh(
    new BoxGeometry(monkeSize, monkeSize, monkeSize),
    new MeshBasicMaterial({ map: monkeTexture })
  )
  const monke = new Monke(mesh, x, y, z);

  scene.add(monke.mesh);
  return monke
}
const monkes = Array(500).fill().map(() => addMonke(MathUtils.randFloatSpread(10*dist),
MathUtils.randFloatSpread(10*dist),MathUtils.randFloatSpread(10*dist)));
//const monke = addMonke(0,10,100)
//const monke2 = addMonke(0,0,1)

const sigma = 10.0
const rho = 28.0
const beta = 8.0 / 3.0
const dt = 5e-3
// Animate function
function animate() {
  requestAnimationFrame(animate);

  monkes.forEach( monke => {
    monke.mesh.rotation.x += monke.v_x;
    monke.mesh.rotation.y += monke.v_y;
    monke.mesh.rotation.z += monke.v_z;
    var x = monke.x / dist
    var y = monke.y / dist
    var z = monke.z / dist
    monke.x = monke.x + dist* (dt*sigma * (y - x))
    monke.y = monke.y + dist* (dt*(x * (rho - z) - y));
    monke.z = monke.z + dist* (dt*(x * y - beta * z));
    monke.mesh.position.x = monke.x + center_x
    monke.mesh.position.y = monke.y + center_y
    monke.mesh.position.z = monke.z + center_z

  })
  controls.update();

  renderer.render(scene, camera);
}

animate()