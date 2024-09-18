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

//const backgroundTexture = new TextureLoader().load('resources/img/exodo.jpg');
//scene.background = backgroundTexture

const dist = 10.0
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
  constructor(mesh,x, y, z, v, r) {
    this.mesh = mesh;
    this.v_x = v[0];
    this.v_y = v[1];
    this.v_z = v[2];
    this.r_x = r[0];
    this.r_y = r[1];
    this.r_z = r[2];
    this.x = x;
    this.y = y;
    this.z = z;
    //this.label = new TextGeometry(`${x}, ${y}, ${z}`);
    mesh.position.set(x + center_x,y + center_y,z + center_z);
  }
}

class TorusBox {
  constructor(l_x,r_x,l_y,r_y,l_z,r_z) {
    this.l_x = l_x
    this.r_x = r_x
    this.l_y = l_y
    this.r_y = r_y
    this.l_z = l_z
    this.r_z = r_z
  }

  apply(object) {
    if (object.position.x < this.l_x) {
      object.position.x = this.r_x
    }
    else if (this.r_x < object.position.x) {
      object.position.x = this.l_x
    }
    if (object.position.y < this.l_y) {
      object.position.y = this.r_y
    }
    else if (this.r_y < object.position.y) {
      object.position.y = this.l_y
    }
    if (object.position.z < this.l_z) {
      object.position.z = this.r_z
    }
    else if (this.r_z < object.position.z) {
      object.position.z = this.l_z
    }
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
const VEL = 10
const N_FILES = 20
const N_MARIOS = 5
const v_x = MathUtils.randFloatSpread(VEL);
const v_y = MathUtils.randFloatSpread(VEL);
const v_z = MathUtils.randFloatSpread(VEL);
const r_x = 0;
const r_y = MathUtils.randFloatSpread(0.1);
const r_z = 0;
const r = [r_x, r_y, r_z]
const v = [v_x, v_y, v_z]
const g_x = MathUtils.randFloatSpread(0.05);

function addMarioMesh(n, m, v, z) {
  var marios = Array.from(Array(n*m).keys()).map(i => addMario((i%n)*dist*dist, Math.floor(i/m)*dist*dist, z, v, r));
  return marios
}

function addMario(x,y,z, v,r) {
  const marioSize = MathUtils.randFloat(dist, 2*dist)+dist;
  const marioTexture = new TextureLoader().load(`resources/img/la_zorra.jpeg`);
  const mesh = new Mesh(
    new BoxGeometry(marioSize, marioSize, marioSize),
    new MeshBasicMaterial({ map: marioTexture })
  )
  const mario = new Mario(mesh, x, y, z, v, r);

  scene.add(mario.mesh);
  return mario
}

// TorusBox
const CYCLE = false
var r_b
if (CYCLE) {
  r_b = N_MARIOS*N_MARIOS*dist
} else {
  r_b = N_MARIOS*dist*dist
}
const l_b = -r_b
const torusBox = new TorusBox(l_b,r_b,l_b,r_b,l_b,r_b)

const marioTensor = [addMarioMesh(N_MARIOS,N_MARIOS,v, 0.0)];
for (var i = 0; i < N_MARIOS-1; ++i) {
  marioTensor.push(addMarioMesh(N_MARIOS,N_MARIOS,v, (i+1)*dist*dist))
}

//const mario = addMario(0,10,100)
//const mario2 = addMario(0,0,1)

const sigma = 10.0
const rho = 28.0
const beta = 8.0 / 3.0
const dt = 2e-3
// Animate function
function animate() {
  requestAnimationFrame(animate);
  marioTensor.forEach(marios => {
    marios.forEach(mario => {
      mario.mesh.position.x += mario.v_x;
      mario.mesh.position.y += mario.v_y;
      mario.mesh.position.z += mario.v_z;
      mario.mesh.rotation.x += mario.r_x;
      mario.mesh.rotation.y += mario.r_y;
      mario.mesh.rotation.z += mario.r_z;
      torusBox.apply(mario.mesh)
    })
  })

  controls.update();
  renderer.render(scene, camera);
}

animate()