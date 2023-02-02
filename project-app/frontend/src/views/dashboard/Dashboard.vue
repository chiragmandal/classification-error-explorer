<template>
  <v-container
    id="dashboard"
    fluid
    tag="section"
  >
    <v-row>
      <v-col
        cols="1"
        lg="6"
      >
        <h1 style="font-weight: bold">
          Select a misclassified image to review
        </h1>
      </v-col>
    </v-row>
    <v-row style="height: 30px" />
    <v-row>
      <v-sheet
        class="mx-auto"
        max-width="100%"
      >
        <v-slide-group>
          <v-slide-item
            v-for="img in misclassified"
            :key="img.IMG.IDX"
            v-slot="{ active }"
          >
            <v-card
              :color="active ? undefined : 'grey lighten-1'"
              class="ma-4"
              height="125"
              width="125"
              @click="onUserSelection(img)"
            >
              <img
                :src="'data:image/png;charset=UTF-8;base64,' + img.IMG.IMG_DATA"
                :alt="img.IMG.IDX"
                height="125"
                width="125"
              >
              <v-row
                class="fill-height"
                align="center"
                justify="center"
              >
                <v-scale-transition>
                  <v-icon
                    v-if="active"
                    color="white"
                    size="48"
                    v-text="'mdi-close-circle-outline'"
                  />
                </v-scale-transition>
              </v-row>
            </v-card>
          </v-slide-item>
        </v-slide-group>
      </v-sheet>
    </v-row>
    <v-row style="height: 35px" />
    <v-row
      align="center"
      justify="center"
    >
      <v-pagination
        v-model="batchNo"
        :length="numPages"
        :total-visible="10"
        @next="paginate"
        @previous="paginate"
        @input="paginate"
      />
    </v-row>
    <v-row style="height: 20px" />
    <v-row style="height: 20px" />
    <v-row style="height: 30px" />
    <v-row v-if="currImg">
      <v-col
        cols="4"
        lg="6"
      >
        <h1 style="font-weight: bold">
          Selected Image
        </h1>
      </v-col>
      <v-col
        cols="4"
        lg="3"
      >
        <h1 style="font-weight: bold">
          Image Information
        </h1>
      </v-col>
      <v-col
        cols="4"
        lg="3"
      >
        <h1 style="font-weight: bold">
          Actions to take on Image
        </h1>
      </v-col>
    </v-row>
    <v-row style="height: 30px" />
    <v-row v-if="currImg">
      <v-col
        cols="4"
        lg="6"
      >
        <v-img
          :src="'data:image/png;charset=UTF-8;base64,' + currImg.IMG.IMG_DATA"
          :alt="currImg.IMG.IDX"
          height="450"
          contain
        />
      </v-col>
      <v-col
        cols="4"
        lg="3"
      >
        <v-container>
          <v-row>
            <v-col
              cols="2"
              lg="5"
            >
              <p
                class="d-inline-flex font-weight-light ml-2 mt-1 font-weight-bold"
                style="font-size: 18px"
              >
                Assigned Class:
              </p>
            </v-col>
            <v-col
              cols="2"
              lg="7"
            >
              <p
                class="d-inline-flex font-weight-light ml-2 mt-1"
                style="font-size: 18px"
              >
                {{ currImg.IMG.CLASS_PRED }}
              </p>
            </v-col>
          </v-row>
          <v-row>
            <v-col
              cols="2"
              lg="5"
            >
              <p
                class="d-inline-flex font-weight-light ml-2 mt-1 font-weight-bold"
                style="font-size: 18px"
              >
                Expected Class:
              </p>
            </v-col>
            <v-col
              cols="2"
              lg="7"
            >
              <p
                class="d-inline-flex font-weight-light ml-2 mt-1"
                style="font-size: 18px"
              >
                {{ currImg.IMG.CLASS_ACTUAL }}
              </p>
            </v-col>
          </v-row>
          <v-row style="height: 30px" />
          <v-row>
            <v-dialog
              v-model="similarityDialog"
              :disabled="!buttonActive"
              width="1250"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  color="blue"
                  dark
                  width="250"
                  v-bind="attrs"
                  v-on="on"
                >
                  View Similar Images
                </v-btn>
              </template>
              <v-card>
                <v-card-title class="text-h5 grey lighten-2">
                  Similar Images
                </v-card-title>
                <v-divider />
                <v-container fluid>
                  <v-row
                    align="center"
                    justify="center"
                  >
                    <v-col
                      cols="2"
                      sm="4"
                    >
                      <v-row>
                        <p
                          class="d-inline-flex font-weight-light ml-2 mt-1 font-weight-bold"
                          style="font-size: 18px"
                        >
                          Selected Image
                        </p>
                      </v-row>
                      <v-row>
                        <v-img
                          :src="'data:image/png;charset=UTF-8;base64,' + currImg.IMG.IMG_DATA"
                          :alt="currImg.IMG.IDX"
                          height="450"
                          contain
                        />
                      </v-row>
                    </v-col>
                    <v-col
                      cols="2"
                      sm="8"
                    >
                      <v-row v-if="similarAssigned">
                        <p
                          class="d-inline-flex font-weight-light ml-2 mt-1 font-weight-bold"
                          style="font-size: 18px"
                        >
                          Top-5 of Predicted Class--:-- {{ currImg.IMG.CLASS_PRED }}
                        </p>
                      </v-row>
                      <v-divider />
                      <v-row
                        v-if="similarAssigned"
                        dense
                        style="overflow-x: auto; white-space: nowrap;"
                        align="center"
                        justify="center"
                      >
                        <v-col
                          v-for="pred in similarAssigned"
                          :key="pred.IMG.IDX"
                          cols="12"
                          sm="6"
                          lg="2"
                          style="display: inline-block; margin: 0; vertical-align: middle;"
                        >
                          <v-img
                            :src="'data:image/png;charset=UTF-8;base64,' + pred.IMG.IMG_DATA"
                            :alt="pred.IMG.IDX"
                            height="270"
                            contain
                            @click="setImageToEnlarge('data:image/png;charset=UTF-8;base64,' + pred.IMG.IMG_DATA)"
                          />
                          <p>{{ pred.IMG.SIM_SCORE }}</p>
                        </v-col>
                        <v-dialog
                          v-model="gotSmallImage"
                          max-width="500"
                          style="z-index:20001;"
                          overlay-color="black"
                        >
                          <v-card
                            @click="unsetImageToEnlarge()"
                          >
                            <v-img
                              :src="imageToEnlarge"
                              max-width="500"
                              max-height="500"
                              contain
                            />
                          </v-card>
                        </v-dialog>
                      </v-row>
                      <v-row style="height: 30px" />
                      <v-row v-if="similarExpected">
                        <p
                          class="d-inline-flex font-weight-light ml-2 mt-1 font-weight-bold"
                          style="font-size: 18px"
                        >
                          Top-5 of Expected Class--:-- {{ currImg.IMG.CLASS_ACTUAL }}
                        </p>
                      </v-row>
                      <v-row v-if="!similarExpected">
                        <p
                          class="d-inline-flex font-weight-light ml-2 mt-1 font-weight-bold"
                          style="font-size: 18px"
                        >
                          Expected Class--:-- {{ currImg.IMG.CLASS_ACTUAL }}. No results for Similar Images.
                        </p>
                      </v-row>
                      <v-divider />
                      <v-row
                        v-if="similarExpected"
                        dense
                        style="overflow-x: auto; white-space: nowrap;"
                        align="center"
                        justify="center"
                      >
                        <v-col
                          v-for="actual in similarExpected"
                          :key="actual.IMG.IDX"
                          cols="12"
                          sm="6"
                          lg="2"
                          style="display: inline-block; margin: 0; vertical-align: middle;"
                        >
                          <v-img
                            :src="'data:image/png;charset=UTF-8;base64,' + actual.IMG.IMG_DATA"
                            :alt="actual.IMG.IDX"
                            height="300"
                            contain
                            @click="setImageToEnlarge('data:image/png;charset=UTF-8;base64,' + actual.IMG.IMG_DATA)"
                          />
                          <p>
                            {{ actual.IMG.SIM_SCORE }}
                          </p>
                        </v-col>
                        <v-dialog
                          v-model="gotSmallImage"
                          max-width="500"
                          style="z-index:20001;"
                          overlay-color="black"
                        >
                          <v-card
                            @click="unsetImageToEnlarge()"
                          >
                            <v-img
                              :src="imageToEnlarge"
                              max-width="500"
                              max-height="500"
                              contain
                            />
                          </v-card>
                        </v-dialog>
                      </v-row>
                    </v-col>
                  </v-row>
                </v-container>
                <v-row style="height: 30px" />
                <v-row style="height: 40px" />
              </v-card>
            </v-dialog>
          </v-row>
          <v-row style="height: 30px" />
          <v-row style="height: 40px" />
          <v-row>
            <v-dialog
              v-model="explanationDialog"
              :disabled="!buttonActive"
              width="1250"
            >
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  color="blue"
                  dark
                  width="250"
                  v-bind="attrs"
                  v-on="on"
                >
                  View Explanation
                </v-btn>
              </template>
              <v-card>
                <v-card-title class="text-h5 grey lighten-2">
                  Result Explanation
                </v-card-title>
                <v-divider />
                <v-container fluid>
                  <v-row
                    align="center"
                    justify="center"
                  >
                    <v-col
                      cols="2"
                      sm="4"
                    >
                      <v-row>
                        <p
                          class="d-inline-flex font-weight-light ml-2 mt-1 font-weight-bold"
                          style="font-size: 18px"
                        >
                          Selected Image
                        </p>
                      </v-row>
                      <v-row>
                        <v-img
                          :src="'data:image/png;charset=UTF-8;base64,' + currImg.IMG.IMG_DATA"
                          :alt="currImg.IMG.IDX"
                          height="450"
                          contain
                        />
                      </v-row>
                    </v-col>
                    <v-col>
                      <v-row style="height: 20px" />
                      <v-row v-if="explanationImgPred">
                        <p
                          class="d-inline-flex font-weight-light ml-2 mt-1 font-weight-bold"
                          style="font-size: 18px"
                        >
                          Predicted Class--:-- {{ currImg.IMG.CLASS_PRED }}
                        </p>
                      </v-row>
                      <v-divider />
                      <v-row
                        dense
                        style="overflow-x: auto; white-space: nowrap;"
                        align="center"
                        justify="center"
                      >
                        <v-col
                          v-for="exp in explanationImgPred"
                          :key="exp.IMG.IDX"
                          cols="12"
                          sm="6"
                          lg="2"
                          style="display: inline-block; margin: 0; vertical-align: middle;"
                        >
                          <v-img
                            :src="'data:image/png;charset=UTF-8;base64,' + exp.IMG.IMG_DATA"
                            :alt="exp.IMG.IDX"
                            height="270"
                            contain
                            @click="setImageToEnlarge('data:image/png;charset=UTF-8;base64,' + exp.IMG.IMG_DATA)"
                          />
                          <p>
                            {{ exp.IMG.LAYER_NO }}
                          </p>
                        </v-col>
                        <v-dialog
                          v-model="gotSmallImage"
                          max-width="500"
                          style="z-index:20001;"
                          overlay-color="black"
                        >
                          <v-card
                            @click="unsetImageToEnlarge()"
                          >
                            <v-img
                              :src="imageToEnlarge"
                              max-width="500"
                              max-height="500"
                              contain
                            />
                          </v-card>
                        </v-dialog>
                      </v-row>
                      <v-row style="height: 30px" />
                      <v-row v-if="explanationImgActual">
                        <p
                          class="d-inline-flex font-weight-light ml-2 mt-1 font-weight-bold"
                          style="font-size: 18px"
                        >
                          Expected Class--:-- {{ currImg.IMG.CLASS_ACTUAL }}
                        </p>
                      </v-row>
                      <v-row v-if="!explanationImgActual">
                        <p
                          class="d-inline-flex font-weight-light ml-2 mt-1 font-weight-bold"
                          style="font-size: 18px"
                        >
                          Expected Class--:-- {{ currImg.IMG.CLASS_ACTUAL }}. No explanatory results.
                        </p>
                      </v-row>
                      <v-divider />
                      <v-row
                        dense
                        style="overflow-x: auto; white-space: nowrap;"
                        align="center"
                        justify="center"
                      >
                        <v-col
                          v-for="exp in explanationImgActual"
                          :key="exp.IMG.IDX"
                          cols="12"
                          sm="6"
                          lg="2"
                          style="display: inline-block; margin: 0; vertical-align: middle;"
                        >
                          <v-img
                            :src="'data:image/png;charset=UTF-8;base64,' + exp.IMG.IMG_DATA"
                            :alt="exp.IMG.IDX"
                            height="270"
                            contain
                            @click="setImageToEnlarge('data:image/png;charset=UTF-8;base64,' + exp.IMG.IMG_DATA)"
                          />
                          <p>
                            {{ exp.IMG.LAYER_NO }}
                          </p>
                        </v-col>
                        <v-dialog
                          v-model="gotSmallImage"
                          max-width="500"
                          style="z-index:20001;"
                          overlay-color="black"
                        >
                          <v-card
                            @click="unsetImageToEnlarge()"
                          >
                            <v-img
                              :src="imageToEnlarge"
                              max-width="500"
                              max-height="500"
                              contain
                            />
                          </v-card>
                        </v-dialog>
                      </v-row>
                    </v-col>
                  </v-row>
                  <v-row style="height: 40px" />
                </v-container>
              </v-card>
            </v-dialog>
          </v-row>
        </v-container>
      </v-col>
      <v-col
        cols="4"
        lg="3"
      >
        <v-container>
          <v-row>
            <v-col
              cols="2"
              lg="3"
            >
              <v-dialog
                v-model="correctionDialog"
                :disabled="!buttonActive"
                width="500"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    color="blue"
                    dark
                    width="250"
                    v-bind="attrs"
                    v-on="on"
                  >
                    Rectify Image Label
                  </v-btn>
                </template>
                <v-card>
                  <v-card-title class="text-h5 grey lighten-2">
                    Rectify Image Label
                  </v-card-title>
                  <v-card-text>
                    <v-text-field
                      v-model="currCorrectedLabel"
                      label="Correct Label Value"
                      outlined
                    />
                  </v-card-text>
                  <v-divider />
                  <v-card-actions>
                    <v-spacer />
                    <v-btn
                      color="primary"
                      text
                      @click="save_user_actions(1)"
                    >
                      Save
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </v-col>
          </v-row>
          <v-row style="height: 30px" />
          <v-row>
            <v-col
              cols="2"
              lg="3"
            >
              <v-btn
                :disabled="!buttonActive"
                depressed
                color="blue"
                width="250"
                @click="save_user_actions(2)"
              >
                Tag as Out-of-Distribution
              </v-btn>
            </v-col>
          </v-row>
          <v-row style="height: 30px" />
          <v-row>
            <v-col
              cols="2"
              lg="3"
            >
              <v-btn
                :disabled="!buttonActive"
                depressed
                color="blue"
                width="250"
                @click="save_user_actions(3)"
              >
                Add image to Training Set
              </v-btn>
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
    <v-row style="height: 30px" />
    <v-row style="height: 30px" />
    <v-row />
    <v-overlay
      :opacity="1"
      :value="overlay"
    >
      <v-progress-circular
        indeterminate
        size="100"
      >
        Loading
      </v-progress-circular>
    </v-overlay>
  </v-container>
</template>

<script>
  import axios from 'axios'

  export default {
    name: 'Dashboard',

    data: function () {
      return {
        overlay: true,
        batchNo: 1,
        similarAssigned: null,
        similarExpected: null,
        misclassified: null,
        explanationImgPred: null,
        explanationImgActual: null,
        currImg: null,
        correctionDialog: null,
        similarityDialog: null,
        explanationDialog: null,
        currCorrectedLabel: null,
        numPages: 3796, // since total misclassified images are 37955 @Budha
        buttonActive: false,
        imageToEnlarge: null,
        gotSmallImage: false,
      }
    },

    computed: {
      formatString (str) {
        var res = str.replace('_', ' ')
        return this.toUpper(res)
      },

      toUpper (str) {
        return str
          .toLowerCase()
          .split(' ')
          .map(function (word) {
            return word[0].toUpperCase() + word.substr(1)
          })
          .join(' ')
      },
    },

    created: function () {
      this.get_placeholder()
      this.get_misclassified_images()
    },

    methods: {
      log (item) {
        console.log(item)
      },

      onUserSelection (img) {
        this.currImg = img
        this.buttonActive = true
        this.similarAssigned = null
        this.similarExpected = null
        this.call_modules()
      },

      call_modules () {
        this.get_similar_images()
        this.get_explanation()
      },

      get_similar_images () {
        this.similarAssigned = null
        this.similarExpected = null
        axios
          .get('http://localhost:45678/get_similar_images', {
            params: {
              fileID: this.currImg.IMG.IDX,
              classID: this.currImg.IMG.CLASS_PRED_IDX,
            },
          })
          .then((response1) => {
            if (response1 != null && response1.status === 200) {
              this.similarAssigned = response1.data
            }
          })

        axios
          .get('http://localhost:45678/get_similar_images', {
            params: {
              fileID: this.currImg.IMG.IDX,
              classID: this.currImg.IMG.CLASS_ACTUAL_IDX,
            },
          })
          .then((response2) => {
            if (response2 != null && response2.status === 200) {
              this.similarExpected = response2.data
            }
          })
      },

      save_user_actions (actionID) {
        axios
          .get('http://localhost:45678/save_user_action', {
            params: {
              fileID: this.currImg.IMG.IDX,
              userAction: actionID,
              correctedLabel: this.currCorrectedLabel,
            },
          })
          .then((response) => {
          })
        this.correctionDialog = false
        this.currCorrectedLabel = null
      },

      test_api () {
        axios
          .post('http://localhost:45678/get_misclassified_images_batches', {
            params: {
              batchNo: this.batchNo,
            },
          })
          .then(function (response) {
            this.log(response.data)
          })
      },

      get_placeholder () {
        axios
          .get('http://localhost:45678/get_placeholder')
          .then((response) => {
            this.currImg = response.data
          })
      },

      get_explanation () {
        this.explanationImgActual = null
        this.explanationImgPred = null

        axios
          .get('http://localhost:45678/get_explanations', {
            params: {
              fileID: this.currImg.IMG.IDX,
              classID: this.currImg.IMG.CLASS_PRED_IDX,
            },
          })
          .then((response) => {
            if (response != null && response.status === 200) {
              this.explanationImgPred = response.data
            }
          })

        axios
          .get('http://localhost:45678/get_explanations', {
            params: {
              fileID: this.currImg.IMG.IDX,
              classID: this.currImg.IMG.CLASS_ACTUAL_IDX,
            },
          })
          .then((response2) => {
            if (response2 != null && response2.status === 200) {
              this.explanationImgActual = response2.data
            }
          })
      },

      get_misclassified_images () {
        axios
          .get('http://localhost:45678/get_misclassified_images_batches', {
            params: {
              batchNo: this.batchNo,
            },
          })
          .then((response) => {
            this.misclassified = response.data
            this.overlay = false
          })
      },

      paginate () {
        this.get_misclassified_images()
      },

      setImageToEnlarge (input) {
        this.gotSmallImage = true
        this.imageToEnlarge = input
      },

      unsetImageToEnlarge () {
        this.gotSmallImage = false
        this.imageToEnlarge = null
      },
    },
  }
</script>
