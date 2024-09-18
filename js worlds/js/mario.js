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
//scene.add(torus);

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

const backgroundTexture = new TextureLoader().load('resources/img/desert.jpg');
scene.background = backgroundTexture

const dist = 1.0
const center_x = 0.0
const center_y = 0.0
const center_z = -20*dist

function multiply(a, b) {
  var aNumRows = a.length, aNumCols = a[0].length,
      bNumRows = b.length, bNumCols = b[0].length,
      m = new Array(aNumRows);  // initialize array of rows
  for (var r = 0; r < aNumRows; ++r) {
    m[r] = new Array(bNumCols); // initialize the current row
    for (var c = 0; c < bNumCols; ++c) {
      m[r][c] = 0;             // initialize the current cell
      for (var i = 0; i < aNumCols; ++i) {
        m[r][c] += a[r][i] * b[i][c];
      }
    }
  }
  return m;
}

class Mario {
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

    // Generate a rotation matrix
    this.alpha = MathUtils.randFloatSpread(2*Math.PI)
    this.beta = MathUtils.randFloatSpread(2*Math.PI)
    this.gamma = MathUtils.randFloatSpread(2*Math.PI)

    this.yaw = [[Math.cos(this.alpha), -Math.sin(this.alpha), 0.0],
                [Math.sin(this.alpha), -Math.cos(this.alpha), 0.0],
                [0.0, 0.0, 1.0]]
    this.pitch = [[Math.cos(this.beta), 0.0, Math.sin(this.beta)],
                [0.0, 1.0, 0.0],
                [-Math.sin(this.beta), 0.0, Math.cos(this.beta)]]
    this.roll = [[1.0, 0.0, 0.0],
                [0.0, Math.cos(this.gamma), -Math.sin(this.gamma)],
                [0.0, Math.sin(this.gamma), Math.cos(this.gamma)]]
                
    this.rotation = multiply(multiply(this.yaw, this.pitch), this.roll)
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

// Mario
// Add marios
const N_FILES = 20
const N_MARIOS = 100

function addMario(x,y,z) {
  const marioSize = MathUtils.randFloat(dist, 2*dist)+dist;
  var index = MathUtils.randInt(0, N_FILES)
  const marioTexture = new TextureLoader().load(`resources/img/set/${index}.jpeg`);
  const mesh = new Mesh(
    new BoxGeometry(marioSize, marioSize, marioSize),
    new MeshBasicMaterial({ map: marioTexture })
  )
  const mario = new Mario(mesh, x, y, z);

  scene.add(mario.mesh);
  return mario
}
const marios = Array(N_MARIOS).fill().map(() => addMario(MathUtils.randFloatSpread(10*dist),
MathUtils.randFloatSpread(10*dist),MathUtils.randFloatSpread(10*dist)));
//const mario = addMario(0,10,100)
//const mario2 = addMario(0,0,1)

const sigma = 10.0
const rho = 28.0
const beta = 8.0 / 3.0
const dt = 2e-3
// Animate function
function animate() {
  requestAnimationFrame(animate);

  marios.forEach( mario => {
    mario.mesh.rotation.x += mario.v_x;
    mario.mesh.rotation.y += mario.v_y;
    mario.mesh.rotation.z += mario.v_z;
    var x = mario.x / dist
    var y = mario.y / dist
    var z = mario.z / dist
    mario.x = mario.x + dist* (dt*sigma * (y - x))
    mario.y = mario.y + dist* (dt*(x * (rho - z) - y));
    mario.z = mario.z + dist* (dt*(x * y - beta * z));
    // Apply rotation
    mario.mesh.position.x = mario.x + center_x
    mario.mesh.position.y = mario.y + center_y
    mario.mesh.position.z = mario.z + center_z

    console.table([mario.x + center_x, mario.y + center_y, mario.z + center_z])
    var result = multiply(mario.rotation, [[mario.x + center_x], [mario.y + center_y], [mario.z + center_z]])
    mario.mesh.position.x = result[0]
    mario.mesh.position.y = result[1]
    mario.mesh.position.z = result[2]

  })
  controls.update();

  renderer.render(scene, camera);
}

animate()