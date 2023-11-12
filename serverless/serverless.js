import axios from 'axios';
import mongoose from 'mongoose';
import { QuestionModel } from '../models/question';

const MONGO_URL = process.env.MONGODB_URL;
const LEETCODE_API_URL = 'https://leetcode.com/graphql';

async function getQuestionDescription(titleSlug) {
  const response = await axios.get(LEETCODE_API_URL, {
    query: `
      query questionContent($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
          content
          mysqlSchemas
          dataSchemas
        }
      }
    `,
    variables: { titleSlug },
    operationName: 'questionContent',
  });

  return response.data.data.question.content;
}

async function getAllQuestions(limit) {
  const response = await axios.get(LEETCODE_API_URL, {
    query: `
      query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(
          categorySlug: $categorySlug
          limit: $limit
          skip: $skip
          filters: $filters
        ) {
          total: totalNum
          questions: data {
            acRate
            difficulty
            freqBar
            frontendQuestionId: questionFrontendId
            isFavor
            paidOnly: isPaidOnly
            status
            title
            titleSlug
            topicTags {
              name
              id
              slug
            }
            hasSolution
            hasVideoSolution
          }
        }
      }
    `,
    variables: { categorySlug: '', skip: 0, limit, filters: {} },
  });

  const questions = response.data.data.problemsetQuestionList.questions;

  const processed = [];

  for (const question of questions) {
    if (question.paidOnly) {
      continue;
    }

    const current = {
      id: question.frontendQuestionId,
      title: question.title,
      categories: question.topicTags.map((tag) => tag.name),
      complexity: question.difficulty,
      link: `https://leetcode.com/problems/${question.titleSlug}`,
      description: await getQuestionDescription(question.titleSlug),
    };

    processed.push(current);
  }

  return processed;
}

async function populate(limit) {
  await mongoose.connect(MONGO_URL, { useNewUrlParser: true, useUnifiedTopology: true });
  const db = mongoose.connection;

  db.once('open', async () => {
    // Assuming YourExistingSchema represents your existing schema
    const ExistingSchema = QuestionModel;

    const questions = await getAllQuestions(limit);

    // Clear existing data
    await ExistingSchema.deleteMany({});

    // Insert new data
    await ExistingSchema.insertMany(questions);

    console.log('Data populated successfully!');

    // Close the Mongoose connection
    mongoose.connection.close();
  });
}

module.exports = { populate };

