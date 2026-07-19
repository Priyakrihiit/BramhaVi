// API Routes Register - Placeholder
// Purpose: Binds REST routes to controller handlers with security gates.

import { Router } from 'express';
import { getPage, updatePageLayout } from '../controllers/page.controller';

const router = Router();

router.get('/pages/:slug', getPage);
router.put('/pages/:id', updatePageLayout);

export default router;
